using Application.Models;
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
    public async Task<IActionResult> Send(Guid id, [FromBody] MessageRequest request)
    {
        try
        {
            var response = await _conversationService.SendMessageAsync(id, request.Content);
            return Ok(new { response });
        }
        catch (KeyNotFoundException)
        {
            return NotFound();
        }
    }

    [HttpPost("{id}/stream")]
    public async Task Stream(Guid id, [FromBody] MessageRequest request)
    {
        Response.Headers.Append("Content-Type", "text/event-stream");
        Response.Headers.Append("Cache-Control", "no-cache");
        Response.Headers.Append("Connection", "keep-alive");

        try
        {
            await foreach (var chunk in _conversationService.StreamMessageAsync(id, request.Content))
            {
                // SSE events must start with "data:" and end with double newlines
                await Response.WriteAsync($"data: {chunk}\n\n");
                await Response.Body.FlushAsync();
            }

            // Signal end of stream
            await Response.WriteAsync("event: end\n\n");
            await Response.Body.FlushAsync();
        }
        catch (KeyNotFoundException)
        {
            Response.StatusCode = StatusCodes.Status404NotFound;
            await Response.WriteAsync("event: error\ndata: Conversation not found\n\n");
        }
        catch (Exception ex)
        {
            Response.StatusCode = StatusCodes.Status500InternalServerError;
            await Response.WriteAsync($"event: error\ndata: {ex.Message}\n\n");
        }
    }

}
