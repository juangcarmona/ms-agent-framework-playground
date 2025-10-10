namespace Msaf02Persistence.Domain.Entities;

using System.ComponentModel.DataAnnotations;

public class Conversation
{
    [Key]
    public Guid Id { get; set; } = Guid.NewGuid();
    public string Title { get; set; } = "New conversation";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public string ThreadJson { get; set; } = "{}";
}
