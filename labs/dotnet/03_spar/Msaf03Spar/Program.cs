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

var baseUrl = config["OPENAI_API_BASE"] ?? "http://localhost:12434/engines/llama.cpp/v1";
var apiKey = config["OPENAI_API_KEY"] ?? "none";
var modelId = config["MODEL_ID"] ?? "ai/gpt-oss:latest";

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
var query = Console.ReadLine() ?? "Docker Model Runner and Microsoft Agent Framework";

Echo.System($"Running agentic loop for '{query}' …\n");

var finalText = new System.Text.StringBuilder();

await foreach (var update in agent.RunStreamingAsync(query, thread))
{
    // 1) Aggregate text deltas
    if (!string.IsNullOrEmpty(update.Text))
    {
        Echo.Agent(update.Text);
        finalText.Append(update.Text);
    }

    // 2) Inspect contents
    if (update.Contents is { Count: > 0 })
    {
        foreach (var content in update.Contents)
        {
            switch (content)
            {
                case FunctionCallContent call:
                    string argText = call.Arguments is null
                        ? ""
                        : string.Join(" ", call.Arguments.Select(kv => $"{kv.Key}={FormatArg(kv.Value)}"));
                    Echo.Step($"[ACT] {call.Name} {argText}");
                    break;

                case FunctionResultContent result:
                    string preview = ToPreview(result.Result);
                    Echo.System($"[TOOL] {result.CallId} → {preview}");
                    break;

                case TextContent t:
                    Echo.Agent(t.Text);
                    finalText.Append(t.Text);
                    break;

                default:
                    Echo.Warn($"[?] Unhandled content type: {content.GetType().Name}");
                    break;
            }
        }
    }
}

// 3) After streaming ends, output the reflection/summary
Echo.Done("✅ Reasoning cycle complete");

Echo.Step("🔁 Reflecting on gathered information…");

var prompt = "Now summarize the findings you just gathered in a concise paragraph, highlighting key points and their relationship.";
   
await Echo.StreamAgentAsync(agent.RunStreamingAsync(prompt, thread));



// ────────────────────────────────────────────────────────────────
//  Helper functions (keep in same file below your top-level code)
// ────────────────────────────────────────────────────────────────
static string FormatArg(object? value)
{
    if (value is null) return "null";
    return value switch
    {
        string s => s,
        bool b => b.ToString().ToLowerInvariant(),
        int or long or double or float or decimal => Convert.ToString(value, System.Globalization.CultureInfo.InvariantCulture) ?? "",
        _ => JsonSerializer.Serialize(value)
    };
}

static string ToPreview(object? resultObj, int max = 240)
{
    if (resultObj is null) return "(null)";
    string s = resultObj switch
    {
        string str => str,
        BinaryData bd => bd.ToString(),
        _ => JsonSerializer.Serialize(resultObj)
    };
    return s.Length > max ? s[..max] + "…" : s;
}

