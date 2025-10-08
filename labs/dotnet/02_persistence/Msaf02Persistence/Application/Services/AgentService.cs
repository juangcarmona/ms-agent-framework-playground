using Microsoft.Agents.AI;
using OpenAI;
using System.ClientModel;
using System.Text.Json;

namespace Application.Services;

public class AgentService
{
    private readonly string _model;
    private readonly string _apiKey;
    private readonly string _baseUrl;

    public AgentService(IConfiguration config)
    {
        _apiKey = config["OPENAI_API_KEY"] ?? "none";
        _baseUrl = config["OPENAI_API_BASE"] ?? "http://localhost:12434/engines/llama.cpp/v1";
        _model = config["MODEL_ID"] ?? "ai/gpt-oss:latest";
    }

    private AIAgent CreateAgent()
    {
        var options = new OpenAIClientOptions { Endpoint = new Uri(_baseUrl) };
        var credential = new ApiKeyCredential(_apiKey);
        var client = new OpenAIClient(credential, options);

        var chatClient = client.GetChatClient(_model);

        return chatClient.CreateAIAgent(
            instructions: "You are a friendly local assistant running fully offline.",
            name: "LocalAssistant");
    }

    public async Task<(string response, string threadJson)> RunAsync(string input, string? existingThreadJson)
    {
        var agent = CreateAgent();

        AgentThread thread = string.IsNullOrEmpty(existingThreadJson)
            ? agent.GetNewThread()
            : agent.DeserializeThread(JsonSerializer.Deserialize<JsonElement>(existingThreadJson!));

        var result = await agent.RunAsync(input, thread);
        var serialized = thread.Serialize();
        var json = JsonSerializer.Serialize(serialized);

        return (result.Text, json);
    }

    public async IAsyncEnumerable<string> RunStreamingAsync(string input, string? existingThreadJson)
    {
        var agent = CreateAgent();

        AgentThread thread = string.IsNullOrEmpty(existingThreadJson)
            ? agent.GetNewThread()
            : agent.DeserializeThread(JsonSerializer.Deserialize<JsonElement>(existingThreadJson!));

        await foreach (var update in agent.RunStreamingAsync(input, thread))
            yield return update.Text;
    }
}
