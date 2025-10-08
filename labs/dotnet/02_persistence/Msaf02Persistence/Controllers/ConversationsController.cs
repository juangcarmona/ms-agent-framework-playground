using Application.Services;
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/[controller]")]
public class ConversationsController : ControllerBase
{
    private readonly ConversationService _conversationService;
    private readonly ConversationRepository _repo;

    public ConversationsController(ConversationService conversationService, ConversationRepository repo)
    {
        _conversationService = conversationService;
        _repo = repo;
    }

    [HttpGet]
    public async Task<IActionResult> GetAll() => Ok(await _repo.GetAllAsync());

    [HttpGet("{id}")]
    public async Task<IActionResult> Get(Guid id)
    {
        var c = await _repo.GetAsync(id);
        return c is null ? NotFound() : Ok(c);
    }

    [HttpPost]
    public async Task<IActionResult> Create()
    {
        var c = await _conversationService.CreateConversationAsync();
        return Ok(c);
    }

    [HttpPost("{id}/messages")]
    public async Task<IActionResult> Send(Guid id, [FromBody] string input)
    {
        try
        {
            var response = await _conversationService.SendMessageAsync(id, input);
            return Ok(new { response });
        }
        catch (KeyNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpPost("{id}/stream")]
    public async Task Stream(Guid id, [FromBody] string input)
    {
        Response.Headers.Add("Content-Type", "text/event-stream");

        await foreach (var chunk in _conversationService.StreamMessageAsync(id, input))
        {
            await Response.WriteAsync($"data: {chunk}\n\n");
            await Response.Body.FlushAsync();
        }
    }
}
