using Microsoft.EntityFrameworkCore;

public class ConversationDb : DbContext
{
    public ConversationDb(DbContextOptions<ConversationDb> options) : base(options) { }

    public DbSet<Conversation> Conversations => Set<Conversation>();
    public DbSet<ChatHistoryItem> ChatHistory => Set<ChatHistoryItem>();


    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<ChatHistoryItem>()
            .HasKey(x => x.Id);

        modelBuilder.Entity<ChatHistoryItem>()
            .HasIndex(x => x.ThreadId);
    }
}