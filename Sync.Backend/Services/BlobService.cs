using Azure.Identity;
using Azure.Storage.Blobs;
using Microsoft.Extensions.Options;
using Sync.Backend.Models;

namespace Sync.Backend.Services;

/// <summary>Azure Blob storage service</summary>
public class BlobService
{
    private readonly BlobContainerClient _containerClient;

    public BlobService(IOptions<SyncSettings> options)
    {
        var settings = options.Value;
        var credential = new DefaultAzureCredential();
        var serviceClient = new BlobServiceClient(new Uri(settings.AzureStorageAccountUrl), credential);
        _containerClient = serviceClient.GetBlobContainerClient(settings.AzureStorageContainerName);
    }

    /// <summary>Upload a file (streaming)</summary>
    public async Task UploadAsync(string fileName, Stream data)
    {
        var blobClient = _containerClient.GetBlobClient(fileName);
        await blobClient.UploadAsync(data, overwrite: true);
    }

    /// <summary>Download a file (streaming)</summary>
    public async Task<Stream> DownloadAsync(string fileName)
    {
        var blobClient = _containerClient.GetBlobClient(fileName);
        var response = await blobClient.DownloadStreamingAsync();
        return response.Value.Content;
    }
}
