using Microsoft.EntityFrameworkCore;

public class ConversationDb : DbContext
{
    public ConversationDb(DbContextOptions<ConversationDb> options) : base(options) { }

    public DbSet<Conversation> Conversations => Set<Conversation>();
    public DbSet<Message> Messages => Set<Message>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Conversation>()
            .HasMany(c => c.Messages)
            .WithOne()
            .HasForeignKey(m => m.ConversationId);
    }
}
