namespace Sync.Backend.Services;

/// <summary>Periodically removes expired entries from InMemoryKvService</summary>
public class KvCleanupService : BackgroundService
{
    private static readonly TimeSpan Interval = TimeSpan.FromMinutes(5);

    private readonly InMemoryKvService _kvService;
    private readonly ILogger<KvCleanupService> _logger;

    public KvCleanupService(InMemoryKvService kvService, ILogger<KvCleanupService> logger)
    {
        _kvService = kvService;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        using var timer = new PeriodicTimer(Interval);

        while (await timer.WaitForNextTickAsync(stoppingToken))
        {
            var removed = _kvService.RemoveExpired();
            if (removed > 0)
                _logger.LogInformation("Cleaned up {Count} expired entries", removed);
        }
    }
}
