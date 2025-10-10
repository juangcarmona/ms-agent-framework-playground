namespace Application.Settings;

public sealed class AgentsConfig
{
    public AgentSettings Chat { get; set; } = new();
    public AgentSettings TitleGenerator { get; set; } = new();
}