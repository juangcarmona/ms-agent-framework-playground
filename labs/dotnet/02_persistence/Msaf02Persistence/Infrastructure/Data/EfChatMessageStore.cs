namespace Msaf02Persistence.Infrastructure.Data;

using Microsoft.Agents.AI;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.AI;
using Msaf02Persistence.Domain.Entities;
using System.Text.Json;

internal sealed class EfChatMessageStore : ChatMessageStore
{
    private readonly IDbContextFactory<ConversationDb> _dbFactory;
    public string? ThreadDbKey { get; private set; }

    public EfChatMessageStore(
        IDbContextFactory<ConversationDb> dbFactory,
        JsonElement serializedStoreState,
        JsonSerializerOptions? _ = null)
    {
        _dbFactory = dbFactory ?? throw new ArgumentNullException(nameof(dbFactory));

        if (serializedStoreState.ValueKind is JsonValueKind.String)
            ThreadDbKey = serializedStoreState.GetString();
    }

    public override async Task AddMessagesAsync(IEnumerable<ChatMessage> messages, CancellationToken ct)
    {
        ThreadDbKey ??= Guid.NewGuid().ToString("N");
        await using var db = await _dbFactory.CreateDbContextAsync(ct);

        var now = DateTimeOffset.UtcNow;

        foreach (var m in messages)
        {
            m.AuthorName ??= m.Role == ChatRole.User ? "User" : "Assistant";
            m.CreatedAt ??= now;
            m.MessageId ??= Guid.NewGuid().ToString("N");

            db.ChatHistory.Add(new ChatHistoryItem
            {
                ThreadId = ThreadDbKey,
                Key = $"{ThreadDbKey}-{m.MessageId}",
                Timestamp = m.CreatedAt.Value,
                SerializedMessage = JsonSerializer.Serialize(m),
                MessageText = m.Text
            });
        }

        await db.SaveChangesAsync(ct);
    }

    public override async Task<IEnumerable<ChatMessage>> GetMessagesAsync(CancellationToken ct)
    {
        if (string.IsNullOrEmpty(ThreadDbKey))
            return Enumerable.Empty<ChatMessage>();

        await using var db = await _dbFactory.CreateDbContextAsync(ct);

        var records = await db.ChatHistory
            .Where(x => x.ThreadId == ThreadDbKey)
            .OrderByDescending(x => x.Timestamp)
            .Take(10)
            .ToListAsync(ct);

        records.Reverse();

        return records
            .Select(x => JsonSerializer.Deserialize<ChatMessage>(x.SerializedMessage!)!)
            .ToList();
    }

    public override JsonElement Serialize(JsonSerializerOptions? jsonSerializerOptions = null) =>
        JsonSerializer.SerializeToElement(ThreadDbKey);
}
