namespace Msaf02Persistence.Controllers;

using Msaf02Persistence.Application.Models;
using Msaf02Persistence.Application.Services;
using Microsoft.AspNetCore.Mvc;
using Msaf02Persistence.Domain.Repositories;

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

    [HttpGet("{id}/messages")]
    public async Task<IActionResult> GetMessages(Guid id, CancellationToken ct)
    {
        try
        {
            var (meta, msgs) = await _conversationService.GetConversationAsync(id, ct);
            var result = msgs.Select(m => new
            {
                role = m.Role.ToString(),
                author = m.AuthorName,
                createdAt = m.CreatedAt,
                content = m.Text,
                messageId = m.MessageId
            });
            return Ok(new
            {
                conversationId = meta.Id,
                title = meta.Title,
                createdAt = meta.CreatedAt,
                messages = result
            });
        }
        catch (KeyNotFoundException)
        {
            return NotFound(new { error = "Conversation not found" });
        }
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

    [HttpDelete("{id}")]
    public async Task<IActionResult> Delete(Guid id)
    {
        try
        {
            await _conversationService.DeleteConversationAsync(id);
            return NoContent();
        }
        catch (KeyNotFoundException)
        {
            return NotFound(new { error = "Conversation not found" });
        }
    }
}
