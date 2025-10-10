namespace Application.Settings;

public sealed class OpenAISettings
{
    public string ApiKey { get; set; } = "none";
    public string BaseUrl { get; set; } = "http://model-runner.docker.internal/engines/llama.cpp/v1";
    public string DefaultModel { get; set; } = "ai/gpt-oss:latest";
}