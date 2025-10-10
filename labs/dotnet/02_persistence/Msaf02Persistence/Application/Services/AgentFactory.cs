using Microsoft.Agents.AI;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Options;
using OpenAI;
using System.ClientModel;
using Msaf02Persistence.Infrastructure.Data;
using Application.Settings;

namespace Msaf02Persistence.Application.Services;

public sealed class AgentFactory
{
    private readonly OpenAISettings _openai;
    private readonly AgentsConfig _agents;
    private readonly IDbContextFactory<ConversationDb> _dbFactory;

    public AgentFactory(
        IOptions<OpenAISettings> openai,
        IOptions<AgentsConfig> agents,
        IDbContextFactory<ConversationDb> dbFactory)
    {
        _openai = openai.Value;
        _agents = agents.Value;
        _dbFactory = dbFactory;
    }

    public AIAgent Create(string key = "Chat")
    {
        // Select which agent configuration to use
        var cfg = key.ToLowerInvariant() switch
        {
            "chat" => _agents.Chat,
            "title-generator" => _agents.TitleGenerator,
            _ => _agents.Chat
        };

        // Prepare OpenAI-compatible client
        var options = new OpenAIClientOptions { Endpoint = new Uri(_openai.BaseUrl) };
        var credential = new ApiKeyCredential(_openai.ApiKey);
        var client = new OpenAIClient(credential, options);

        // Create chat client using configured model (or fallback)
        var chatClient = client.GetChatClient(cfg.Model ?? _openai.DefaultModel ?? "ai/gpt-oss:latest");

        // Build agent with persistence through EfChatMessageStore
        var agent = chatClient.CreateAIAgent(new ChatClientAgentOptions
        {
            Name = key,
            Instructions = cfg.Instructions ?? "You are a friendly local assistant running fully offline.",
            ChatMessageStoreFactory = ctx =>
                new EfChatMessageStore(_dbFactory, ctx.SerializedState, ctx.JsonSerializerOptions)
        });

        return agent;
    }
}
