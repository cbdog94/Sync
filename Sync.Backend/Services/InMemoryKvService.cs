using System.Collections.Concurrent;

namespace Sync.Backend.Services;

/// <summary>In-memory key-value store with expiry support</summary>
public class InMemoryKvService
{
    private readonly ConcurrentDictionary<string, (string Value, DateTime? Expiry)> _store = new();

    public Task<string?> GetAsync(string key)
    {
        if (!_store.TryGetValue(key, out var entry))
            return Task.FromResult<string?>(null);

        if (entry.Expiry.HasValue && DateTime.UtcNow > entry.Expiry.Value)
            return Task.FromResult<string?>(null);

        return Task.FromResult<string?>(entry.Value);
    }

    public Task<Dictionary<string, string>> GetManyAsync(IReadOnlyList<string> keys)
    {
        var result = new Dictionary<string, string>();
        var now = DateTime.UtcNow;

        foreach (var key in keys)
        {
            if (!_store.TryGetValue(key, out var entry)) continue;

            if (entry.Expiry.HasValue && now > entry.Expiry.Value)
                continue;

            result[key] = entry.Value;
        }

        return Task.FromResult(result);
    }

    public int RemoveExpired()
    {
        var now = DateTime.UtcNow;
        var count = 0;
        foreach (var kvp in _store)
        {
            if (kvp.Value.Expiry.HasValue && now > kvp.Value.Expiry.Value)
            {
                if (_store.TryRemove(kvp.Key, out _))
                    count++;
            }
        }
        return count;
    }

    public Task SetAsync(string key, string value, int expirySeconds = 3600)
    {
        var expiry = DateTime.UtcNow.AddSeconds(expirySeconds);
        _store[key] = (value, expiry);
        return Task.CompletedTask;
    }

    public Task SetManyAsync(Dictionary<string, string> items, int expirySeconds = 3600)
    {
        var expiry = DateTime.UtcNow.AddSeconds(expirySeconds);
        foreach (var (key, value) in items)
            _store[key] = (value, expiry);
        return Task.CompletedTask;
    }

    public Task DeleteAsync(string key)
    {
        _store.TryRemove(key, out _);
        return Task.CompletedTask;
    }

    public Task DeleteManyAsync(IReadOnlyList<string> keys)
    {
        foreach (var key in keys)
            _store.TryRemove(key, out _);
        return Task.CompletedTask;
    }
}
