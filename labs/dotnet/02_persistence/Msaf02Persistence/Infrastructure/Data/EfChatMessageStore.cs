using Microsoft.Agents.AI;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.AI;
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

        foreach (var m in messages)
        {
            var id = string.IsNullOrEmpty(m.MessageId) ? Guid.NewGuid().ToString("N") : m.MessageId;
            db.ChatHistory.Add(new ChatHistoryItem
            {
                ThreadId = ThreadDbKey,
                Key = $"{ThreadDbKey}-{id}",
                Timestamp = DateTimeOffset.UtcNow,
                SerializedMessage = JsonSerializer.Serialize(m),
                MessageText = m.Text
            });
            ;
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

        records.Reverse(); // chronological order

        return records
            .Select(x => JsonSerializer.Deserialize<ChatMessage>(x.SerializedMessage!)!)
            .ToList();
    }

    public override JsonElement Serialize(JsonSerializerOptions? jsonSerializerOptions = null) =>
        JsonSerializer.SerializeToElement(ThreadDbKey);

   
}
