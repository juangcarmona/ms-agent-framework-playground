namespace Application.Settings;

public sealed class AgentSettings
{
    public string Model { get; set; } = "ai/gpt-oss:latest";
    public string Instructions { get; set; } = "";
}