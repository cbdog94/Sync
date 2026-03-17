namespace Sync.Backend.Models;

/// <summary>Application settings</summary>
public class SyncSettings
{
    /// <summary>Azure Storage account URL</summary>
    public string AzureStorageAccountUrl { get; set; } = "";

    /// <summary>Azure Storage container name</summary>
    public string AzureStorageContainerName { get; set; } = "sync-files";

    /// <summary>Text expiry time in seconds</summary>
    public int TextExpirySeconds { get; set; } = 3600;
}
