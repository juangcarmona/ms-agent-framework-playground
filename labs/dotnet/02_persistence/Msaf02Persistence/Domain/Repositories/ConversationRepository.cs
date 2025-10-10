namespace Msaf02Persistence.Domain.Repositories;

using Microsoft.EntityFrameworkCore;
using Msaf02Persistence.Domain.Entities;
using Msaf02Persistence.Infrastructure.Data;

public class ConversationRepository
{
    private readonly ConversationDb _db;
    public ConversationRepository(ConversationDb db) => _db = db;

    public async Task<Conversation> CreateAsync(Conversation c)
    {
        _db.Conversations.Add(c);
        await _db.SaveChangesAsync();
        return c;
    }

    public async Task<IEnumerable<Conversation>> GetAllAsync() =>
        await _db.Conversations.ToListAsync();

    public async Task<Conversation?> GetAsync(Guid id) =>
        await _db.Conversations.FirstOrDefaultAsync(x => x.Id == id);

    public async Task UpdateAsync(Conversation c)
    {
        _db.Update(c);
        await _db.SaveChangesAsync();
    }
}
