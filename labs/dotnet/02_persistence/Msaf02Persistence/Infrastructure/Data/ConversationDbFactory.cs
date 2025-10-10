using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;

public sealed class ConversationDbFactory : IDesignTimeDbContextFactory<ConversationDb>
{
    public ConversationDb CreateDbContext(string[] args)
    {
        // Locate appsettings.json relative to the current directory
        var basePath = Directory.GetCurrentDirectory();

        var config = new ConfigurationBuilder()
            .SetBasePath(basePath)
            .AddJsonFile("appsettings.json", optional: true)
            .AddEnvironmentVariables()
            .Build();

        var connectionString = config.GetConnectionString("DefaultConnection")
            ?? config["POSTGRES_CONNECTION_STRING"]
            ?? "Host=db;Database=maf;Username=postgres;Password=postgres";

        var optionsBuilder = new DbContextOptionsBuilder<ConversationDb>();
        optionsBuilder.UseNpgsql(connectionString);

        return new ConversationDb(optionsBuilder.Options);
    }
}
