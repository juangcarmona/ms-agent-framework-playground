using Application.Models;
using Application.Services;

public class ConversationService
{
    private readonly ConversationRepository _repo;
    private readonly AgentService _agent;

    public ConversationService(ConversationRepository repo, AgentService agent)
    {
        _repo = repo;
        _agent = agent;
    }

    /// <summary>
    /// Creates a new conversation and returns a DTO with its ID and initial state.
    /// </summary>
    public async Task<CreateConversationResult> CreateConversationAsync(string? title = null)
    {
        var conversation = new Conversation
        {
            Title = title ?? "New Conversation",
            CreatedAt = DateTime.UtcNow,
            ThreadJson = "{}" // Empty thread
        };

        var created = await _repo.CreateAsync(conversation);

        return new CreateConversationResult
        {
            ConversationId = created.Id,
            Title = created.Title,
            CreatedAt = created.CreatedAt
        };
    }

    public async Task<ConversationResult> SendMessageAsync(Guid conversationId, string input)
    {
        var conversation = await _repo.GetAsync(conversationId)
            ?? throw new KeyNotFoundException("Conversation not found");

        // Persist user message
        conversation.Messages.Add(new Message { ConversationId = conversationId, Role = "user", Content = input });

        // Run agent
        var (response, threadJson) = await _agent.RunAsync(input, conversation.ThreadJson);

        // Persist assistant message + new thread
        conversation.ThreadJson = threadJson;
        conversation.Messages.Add(new Message { ConversationId = conversationId, Role = "assistant", Content = response });
        await _repo.UpdateAsync(conversation);

        return new ConversationResult(conversation.Id, response);
    }

    public async IAsyncEnumerable<string> StreamMessageAsync(Guid conversationId, string input)
    {
        var conversation = await _repo.GetAsync(conversationId)
            ?? throw new KeyNotFoundException("Conversation not found");

        conversation.Messages.Add(new Message { ConversationId = conversationId, Role = "user", Content = input });
        await _repo.UpdateAsync(conversation);

        // yield chunks as they arrive
        await foreach (var chunk in _agent.RunStreamingAsync(input, conversation.ThreadJson))
        {
            yield return chunk;
        }

        // Optionally capture full assistant text at end if you buffer it
    }
}
