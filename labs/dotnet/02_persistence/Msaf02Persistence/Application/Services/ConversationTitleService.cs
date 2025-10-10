using Microsoft.EntityFrameworkCore;
using Msaf02Persistence.Domain.Entities;
using Msaf02Persistence.Infrastructure.Data;

namespace Msaf02Persistence.Application.Services;

public sealed class ConversationTitleService
{
    private readonly IDbContextFactory<ConversationDb> _dbFactory;
    private readonly AgentFactory _agentFactory;
    private const string DefaultTitle = "New conversation";

    public ConversationTitleService(IDbContextFactory<ConversationDb> dbFactory, AgentFactory agentFactory)
    {
        _dbFactory = dbFactory;
        _agentFactory = agentFactory;
    }

    public async Task GenerateIfNeededAsync(Guid conversationId, string userInput)
    {
        try
        {
            await using var db = await _dbFactory.CreateDbContextAsync();
            var conv = await db.Conversations.FirstOrDefaultAsync(x => x.Id == conversationId);
            if (conv == null || !ShouldGenerateTitle(conv))
                return;

            // Title Agent is expected to return a short title based on the user input.
            var titleAgent = _agentFactory.Create("title-generator");
            var result = await titleAgent.RunAsync(userInput);
            var newTitle = (result.Text ?? string.Empty).Trim();

            if (!string.IsNullOrEmpty(newTitle))
            {
                conv.Title = newTitle.Length > 100 ? newTitle[..100] : newTitle;
                await db.SaveChangesAsync();
            }
        }
        catch
        {
            // Fire-and-forget: swallow all exceptions to avoid affecting main flow.
            // TODO: At leastwe should log errors.
        }
    }

    public bool ShouldGenerateTitle(Conversation conv)
    {
        return conv.Title == DefaultTitle && (string.IsNullOrWhiteSpace(conv.ThreadJson) || conv.ThreadJson == "{}");
    }
}
