namespace Application.Models;

public class CreateConversationResult
{
    public Guid ConversationId { get; init; }
    public string Title { get; init; } = string.Empty;
    public DateTime CreatedAt { get; init; }

    public CreateConversationResult() { }

    public CreateConversationResult(Guid id, string title, DateTime createdAt)
    {
        ConversationId = id;
        Title = title;
        CreatedAt = createdAt;
    }
}
