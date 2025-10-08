using System.ComponentModel.DataAnnotations;

public class Conversation
{
    [Key]
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Title { get; set; } = "New conversation";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public string ThreadJson { get; set; } = "{}";
    public List<Message> Messages { get; set; } = new();
}
