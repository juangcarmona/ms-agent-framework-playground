namespace Msaf02Persistence.Domain.Entities;

public sealed class ChatHistoryItem
{
    public long Id { get; set; }
    public string? Key { get; set; }
    public string? ThreadId { get; set; }
    public DateTimeOffset? Timestamp { get; set; }
    public string? SerializedMessage { get; set; }
    public string? MessageText { get; set; }
}