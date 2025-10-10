using Microsoft.Agents.AI;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.AI;
using System.Runtime.CompilerServices;
using System.Text.Json;
using Msaf02Persistence.Domain.Entities;
using Msaf02Persistence.Infrastructure.Data;

namespace Msaf02Persistence.Application.Services;

public sealed class ConversationService
{
    private readonly IDbContextFactory<ConversationDb> _dbFactory;
    private readonly AgentFactory _agentFactory;
    private readonly ConversationTitleService _titleService;
    private const string DefaultTitle = "New conversation";

    public ConversationService(
        IDbContextFactory<ConversationDb> dbFactory,
        AgentFactory agentFactory,
        ConversationTitleService titleService)
    {
        _dbFactory = dbFactory;
        _agentFactory = agentFactory;
        _titleService = titleService;
    }

    public async Task<Conversation> CreateConversationAsync(string? title = null)
    {
        await using var db = await _dbFactory.CreateDbContextAsync();
        var conv = new Conversation
        {
            Title = title ?? DefaultTitle,
            CreatedAt = DateTime.UtcNow,
            ThreadJson = "{}"
        };
        db.Conversations.Add(conv);
        await db.SaveChangesAsync();
        return conv;
    }

    public async Task<string> SendMessageAsync(Guid conversationId, string userInput)
    {
        await using var db = await _dbFactory.CreateDbContextAsync();
        var conv = await db.Conversations.FirstOrDefaultAsync(x => x.Id == conversationId)
                   ?? throw new KeyNotFoundException("Conversation not found");

        // Fire-and-forget background title generation.
        // This runs asynchronously and is intentionally not awaited.
        _ = _titleService.GenerateIfNeededAsync(conversationId, userInput);

        var agent = _agentFactory.Create();
        var thread = string.IsNullOrWhiteSpace(conv.ThreadJson) || conv.ThreadJson == "{}"
            ? agent.GetNewThread()
            : agent.DeserializeThread(JsonSerializer.Deserialize<JsonElement>(conv.ThreadJson!));

        var run = await agent.RunAsync(userInput, thread);
        conv.ThreadJson = JsonSerializer.Serialize(thread.Serialize());
        await db.SaveChangesAsync();

        return run.Text ?? string.Empty;
    }

    public async IAsyncEnumerable<string> StreamMessageAsync(
           Guid conversationId, string userInput, [EnumeratorCancellation] CancellationToken ct = default)
    {
        await using var db = await _dbFactory.CreateDbContextAsync(ct);
        var conv = await db.Conversations.FirstOrDefaultAsync(x => x.Id == conversationId, ct)
                   ?? throw new KeyNotFoundException("Conversation not found");

        // Fire-and-forget background title generation.
        // This runs asynchronously and is intentionally not awaited.
        _ = _titleService.GenerateIfNeededAsync(conversationId, userInput);

        var agent = _agentFactory.Create();
        var thread = string.IsNullOrWhiteSpace(conv.ThreadJson) || conv.ThreadJson == "{}"
            ? agent.GetNewThread()
            : agent.DeserializeThread(JsonSerializer.Deserialize<JsonElement>(conv.ThreadJson!));

        await foreach (var update in agent.RunStreamingAsync(userInput, thread, cancellationToken: ct))
        {
            var text = update.Text;
            if (!string.IsNullOrEmpty(text))
                yield return text;
        }

        conv.ThreadJson = JsonSerializer.Serialize(thread.Serialize());
        await db.SaveChangesAsync(ct);
    }
    
    public async Task<(Conversation Meta, IReadOnlyList<ChatMessage> Messages)> GetConversationAsync(
        Guid id, CancellationToken ct = default)
    {
        await using var db = await _dbFactory.CreateDbContextAsync(ct);
        var conv = await db.Conversations.FirstOrDefaultAsync(x => x.Id == id, ct)
                   ?? throw new KeyNotFoundException("Conversation not found");

        var threadKey = TryExtractThreadKey(conv.ThreadJson);

        List<ChatMessage> msgs = new();
        if (!string.IsNullOrEmpty(threadKey))
        {
            var items = await db.ChatHistory
                .Where(x => x.ThreadId == threadKey)
                .OrderBy(x => x.Timestamp)
                .ToListAsync(ct);

            // Deserialize back into ChatMessage for API response
            msgs = items
                .Select(x => JsonSerializer.Deserialize<ChatMessage>(x.SerializedMessage!)!)
                .ToList();
        }

        return (conv, msgs);
    }

    private static string? TryExtractThreadKey(string threadJson)
    {
        if (string.IsNullOrWhiteSpace(threadJson))
            return null;

        try
        {
            using var doc = JsonDocument.Parse(threadJson);
            var root = doc.RootElement;

            if (root.ValueKind == JsonValueKind.Object)
            {
                if (root.TryGetProperty("storeState", out var v) && v.ValueKind == JsonValueKind.String)
                    return v.GetString();
            }
        }
        catch
        {
            // ignore malformed JSON
        }

        return null;
    }

    public async Task DeleteConversationAsync(Guid id)
    {
        await using var db = await _dbFactory.CreateDbContextAsync();
        var conv = await db.Conversations.FirstOrDefaultAsync(x => x.Id == id);
        if (conv == null)
            throw new KeyNotFoundException("Conversation not found");
        var threadKey = TryExtractThreadKey(conv.ThreadJson);
        if (!string.IsNullOrEmpty(threadKey))
        {
            var messages = db.ChatHistory.Where(x => x.ThreadId == threadKey);
            db.ChatHistory.RemoveRange(messages);
        }

        db.Conversations.Remove(conv);
        await db.SaveChangesAsync();
    }
}
