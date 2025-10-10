using Microsoft.Agents.AI;
using Microsoft.EntityFrameworkCore;
using OpenAI;
using System.ClientModel;

namespace Application.Services;

public sealed class AgentFactory
{
    private readonly IConfiguration _config;
    private readonly IDbContextFactory<ConversationDb> _dbFactory;

    private readonly string _model;
    private readonly string _apiKey;
    private readonly string _baseUrl;

    public AgentFactory(IConfiguration config, IDbContextFactory<ConversationDb> dbFactory)
    {
        _config = config;
        _dbFactory = dbFactory;

        _apiKey = _config["OPENAI_API_KEY"] ?? "none";
        _baseUrl = _config["OPENAI_API_BASE"] ?? "http://model-runner.docker.internal/engines/llama.cpp/v1";
        _model = _config["MODEL_ID"] ?? "ai/gpt-oss:latest";
    }

    public AIAgent Create()
    {
        // Initialize OpenAI-compatible client using base URL + key
        var options = new OpenAIClientOptions { Endpoint = new Uri(_baseUrl) };
        var credential = new ApiKeyCredential(_apiKey);
        var client = new OpenAIClient(credential, options);

        // Create the chat client for the selected model
        var chatClient = client.GetChatClient(_model);

        // Build agent with persistence via EfChatMessageStore
        var agent = chatClient.CreateAIAgent(new ChatClientAgentOptions
        {
            Name = "LocalAssistant",
            Instructions = "You are a friendly local assistant running fully offline.",
            ChatMessageStoreFactory = ctx =>
                new EfChatMessageStore(_dbFactory, ctx.SerializedState, ctx.JsonSerializerOptions)
        });

        return agent;
    }
}
