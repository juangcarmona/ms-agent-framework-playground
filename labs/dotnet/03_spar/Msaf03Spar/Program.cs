// Lab 03 – Agentic Reasoning 🧩
// A Microsoft Agent Framework research agent senses, plans, acts and reflects
// using local models (Docker Model Runner) and real MCP tools.

using Labs.Shared.Utils;
using Microsoft.Extensions.AI;
using Microsoft.Extensions.Configuration;
using ModelContextProtocol.Client;
using ModelContextProtocol.Protocol;
using OpenAI;
using System.ClientModel;
using System.Text.Json;

// ────────────────────────────────────────────────────────────────
//  1.  Environment  &  Local Model
// ────────────────────────────────────────────────────────────────
Echo.Info("Lab 03 – Agentic Reasoning (Sense → Plan → Act → Reflect)");

var config = new ConfigurationBuilder()
    .AddEnvironmentVariables()
    .AddJsonFile(".env", optional: true)
    .AddUserSecrets<Program>(optional: true)
    .Build();

var apiKey = config["OPENAI_API_KEY"] ?? "none";
var baseUrl = config["OPENAI_API_BASE"] ?? "http://localhost:12434/engines/llama.cpp/v1";
var modelId = config["MODEL_ID"] ?? "ai/gpt-oss";
//var baseUrl = config["OPENAI_API_BASE"] ?? "http://model-runner.docker.internal/engines/llama.cpp/v1";
//var modelId = config["MODEL_ID"] ?? "ai/qwen3:14B-Q6_K";

Echo.System($"Endpoint   : {baseUrl}");
Echo.System($"Model     : {modelId}");

var client = new OpenAIClient(new ApiKeyCredential(apiKey),
                              new OpenAIClientOptions { Endpoint = new Uri(baseUrl) });
var chatClient = client.GetChatClient(modelId);

// ────────────────────────────────────────────────────────────────
//  2.  Connect  MCP Tools (DuckDuckGo + Fetch)
// ────────────────────────────────────────────────────────────────
Echo.Step("🔧 Starting MCP clients …");

// DuckDuckGo MCP server
await using var duck = await McpClient.CreateAsync(
    new StdioClientTransport(new StdioClientTransportOptions
    {
        Name = "DuckDuckGo",
        Command = "docker",
        Arguments = new[]
        {
            "run", "-i", "--rm", "mcp/duckduckgo"
        }
    }));

// Fetch (Reference) MCP server
await using var fetch = await McpClient.CreateAsync(
    new StdioClientTransport(new StdioClientTransportOptions
    {
        Name = "Fetch",
        Command = "docker",
        Arguments = new[]
        {
            "run", "-i", "--rm", "mcp/fetch"
        }
    }));


// Enumerate tools using the *new* instance API (no extensions)
var duckTools = new List<McpClientTool>();
await foreach (var tool in duck.EnumerateToolsAsync())
    duckTools.Add(tool);

var fetchTools = new List<McpClientTool>();
await foreach (var tool in fetch.EnumerateToolsAsync())
    fetchTools.Add(tool);

// Combine both sets into one AITool[] for the agent
var tools = duckTools.Concat(fetchTools)
                     .Cast<AITool>()
                     .ToArray();

Echo.System($"Registered tools → {string.Join(", ", tools.Select(t => t.Name))}");


// ────────────────────────────────────────────────────────────────
//  3.  Build Agent – internal SPAR reasoning
// ────────────────────────────────────────────────────────────────
var instructions = @"
You are a self-sufficient research agent.
When the user asks about any topic:
1. Sense → identify the topics and their intent.
2. Plan  → decide which tools to call and in what order.
3. Act   → invoke 'search' and 'fetch' tools to gather information.
4. Reflect → verify coverage and summarize findings succinctly.
Always think step-by-step, show progress with short statements before your final answer.
";

var agent = chatClient.CreateAIAgent(instructions: instructions,
                                     name: "ResearchAgent",
                                     tools: tools);

var thread = agent.GetNewThread();

// ────────────────────────────────────────────────────────────────
//  4.  Interactive Streaming Run with Event Logging
// ────────────────────────────────────────────────────────────────
Echo.User("Tell me what you want to research :");
var query = Console.ReadLine();
if (query == string.Empty)
{

    query =  "I need you to combine MAF, " + 
             "brand new Microsoft Agent Framework," +
             "with DMR, Docker Model Runner. " +
             "Is it possible to merge both? Generate a " + 
             "recipe for an experiment of but with .NET";
    Echo.User(query);
}

Echo.System($"Running agentic loop for '{query}' …\n");
await Echo.StreamAgentAsync(agent.RunStreamingAsync(query, thread));

Echo.Done("Reasoning cycle complete");
Echo.System("Press any key to exit …");
Console.ReadKey();


