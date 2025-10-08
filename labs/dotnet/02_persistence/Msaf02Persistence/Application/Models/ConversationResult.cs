namespace Application.Models;

public class ConversationResult
{
    public Guid ConversationId { get; init; }
    public string AssistantReply { get; init; }
    public DateTime Timestamp { get; init; }

    public ConversationResult(Guid conversationId, string assistantReply)
    {
        ConversationId = conversationId;
        AssistantReply = assistantReply;
        Timestamp = DateTime.UtcNow;
    }

    public static ConversationResult From(Guid conversationId, string assistantReply)
        => new(conversationId, assistantReply);
}
