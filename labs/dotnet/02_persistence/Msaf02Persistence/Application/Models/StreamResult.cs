namespace Application.Models;

public class StreamResult
{
    /// <summary>
    /// The conversation identifier the stream belongs to.
    /// </summary>
    public Guid ConversationId { get; init; }

    /// <summary>
    /// The incremental text chunk produced by the assistant.
    /// </summary>
    public string Delta { get; init; }

    /// <summary>
    /// True when the model has finished producing output for this turn.
    /// </summary>
    public bool IsCompleted { get; init; }

    /// <summary>
    /// Optional accumulated text, if you buffer server-side.
    /// </summary>
    public string? FullText { get; init; }

    public StreamResult(Guid conversationId, string delta, bool isCompleted = false, string? fullText = null)
    {
        ConversationId = conversationId;
        Delta = delta;
        IsCompleted = isCompleted;
        FullText = fullText;
    }
}
