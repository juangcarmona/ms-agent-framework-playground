// Lab DN01 – The Awakening 🌅
// A Microsoft Agent Framework ChatAgent comes alive,
// speaking through a local model powered by Docker Model Runner.

using Labs.Shared.Utils;
using Microsoft.Extensions.Configuration;
using OpenAI;
using System.ClientModel;

Echo.Info("Lab DN01 – The Awakening (Local Runtime)");

// Load environment variables from .env (optional)
var config = new ConfigurationBuilder()
    .AddEnvironmentVariables()
    .AddUserSecrets<Program>(optional: true)
    .AddJsonFile(".env", optional: true)
    .Build();

// Default local config (DMR / vLLM style)
var baseUrl = config["OPENAI_API_BASE"] ?? "http://localhost:12434/engines/llama.cpp/v1";
var apiKey = config["OPENAI_API_KEY"] ?? "none";
var modelId = config["MODEL_ID"] ?? "ai/gpt-oss:latest";

Echo.System($"Endpoint: {baseUrl}");
Echo.System($"Model: {modelId}");

var options = new OpenAIClientOptions { Endpoint = new Uri(baseUrl) };
var credential = new ApiKeyCredential(apiKey);
var client = new OpenAIClient(credential, options);

var chatClient = client.GetChatClient(modelId);
var agent = chatClient.CreateAIAgent(
    "You are a friendly local assistant running fully offline.",
    "LocalAssistant");

// --- Synchronous Run ---
var userPrompt = "Explain in one line what a local AI agent is.";
Echo.User(userPrompt);

var result = await agent.RunAsync(userPrompt);
Echo.Agent(result.Text);

// --- Streaming Run ---
userPrompt = "Now explain it in a poetic way, with a sonnet, celebrating local intelligence.";
Echo.User(userPrompt);
await Echo.StreamAgentAsync(agent.RunStreamingAsync(userPrompt));

Echo.Done("🌒 The Awakening complete — your machine just spoke without the cloud.");
Echo.System("Press any key to exit...");
Console.ReadKey();
