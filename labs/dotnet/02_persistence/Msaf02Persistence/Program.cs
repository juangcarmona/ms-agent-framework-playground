using Application.Services;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

// ------------------------------------------------------------
// Infrastructure: Database + Repositories
// ------------------------------------------------------------
var conn = builder.Configuration.GetConnectionString("DefaultConnection");
Console.WriteLine($"🔌 Connection: {conn ?? "NULL"}");

builder.Services.AddDbContextFactory<ConversationDb>(options =>
{
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection"));
});


builder.Services.AddScoped<ConversationRepository>();

// ------------------------------------------------------------
// Application layer
// ------------------------------------------------------------
builder.Services.AddSingleton<AgentFactory>();
builder.Services.AddScoped<ConversationService>();
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddOpenApi();

// ------------------------------------------------------------
// Build app
// ------------------------------------------------------------
var app = builder.Build();

// ------------------------------------------------------------
// Runtime configuration
// ------------------------------------------------------------
if (app.Environment.IsDevelopment())
{
    // Enable OpenAPI at URL/openapi/v1.json
    app.MapOpenApi();
}

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<ConversationDb>();
    db.Database.Migrate();
}

app.UseHttpsRedirection();
// app.UseAuthorization();
app.MapControllers();
app.Run();
