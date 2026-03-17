using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Options;
using Sync.Backend.Models;
using Sync.Backend.Services;
using System.Net.Mime;

namespace Sync.Backend.Controllers;

[ApiController]
[Route("syncbackend")]
public class SyncController : ControllerBase
{
    private const int MaxCodeRetries = 20;

    private readonly InMemoryKvService _kvService;
    private readonly BlobService _blobService;
    private readonly SyncSettings _settings;
    private readonly ILogger<SyncController> _logger;

    public SyncController(
        InMemoryKvService kvService,
        BlobService blobService,
        IOptions<SyncSettings> settings,
        ILogger<SyncController> logger)
    {
        _kvService = kvService;
        _blobService = blobService;
        _settings = settings.Value;
        _logger = logger;
    }

    private static string GenerateCode() => Random.Shared.Next(0, 10000).ToString("D4");

    private async Task<string?> GenerateUniqueCodeAsync(string suffix)
    {
        for (int i = 0; i < MaxCodeRetries; i++)
        {
            var code = GenerateCode();
            if (await _kvService.GetAsync($"{code}_{suffix}") is null)
                return code;
        }
        return null;
    }

    [HttpGet("health")]
    public ActionResult<ApiResponse<HealthResult>> Health()
    {
        return new ApiResponse<HealthResult>
        {
            Code = 0,
            Message = "App is running.",
            Result = new HealthResult()
        };
    }

    [HttpPost("submit")]
    public async Task<ActionResult<ApiResponse<SubmitResult>>> Submit([FromBody] SubmitRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Text))
            return new ApiResponse<SubmitResult> { Code = 1, Message = "Text is required.", Result = new() };

        try
        {
            var code = await GenerateUniqueCodeAsync("text");
            if (code is null)
                return new ApiResponse<SubmitResult> { Code = 1, Message = "Unable to generate unique code, please retry.", Result = new() };

            await _kvService.SetManyAsync(new Dictionary<string, string>
            {
                [$"{code}_text"] = request.Text,
                [$"{code}_once"] = request.Once ? "1" : "0"
            }, _settings.TextExpirySeconds);

            return new ApiResponse<SubmitResult> { Code = 0, Result = new SubmitResult { Code = code } };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Submit error");
            return new ApiResponse<SubmitResult> { Code = 1, Message = "Internal server error.", Result = new() };
        }
    }

    [HttpPost("extract")]
    public async Task<ActionResult<ApiResponse<ExtractResult>>> Extract([FromBody] ExtractRequest request)
    {
        if (string.IsNullOrWhiteSpace(request.Code) || request.Code.Length != 4)
            return new ApiResponse<ExtractResult> { Code = 1, Message = "Invalid code.", Result = new() };

        try
        {
            var results = await _kvService.GetManyAsync([$"{request.Code}_text", $"{request.Code}_once"]);

            if (!results.ContainsKey($"{request.Code}_text"))
                return new ApiResponse<ExtractResult> { Code = 2, Message = "Code does not exist.", Result = new() };

            var text = results[$"{request.Code}_text"];
            results.TryGetValue($"{request.Code}_once", out var once);

            if (once == "1")
                await _kvService.DeleteManyAsync([$"{request.Code}_text", $"{request.Code}_once"]);

            return new ApiResponse<ExtractResult> { Code = 0, Result = new ExtractResult { Text = text } };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Extract error");
            return new ApiResponse<ExtractResult> { Code = 1, Message = "Internal server error.", Result = new() };
        }
    }

    [HttpPost("upload")]
    [RequestSizeLimit(500 * 1024 * 1024)]
    public async Task<ActionResult<ApiResponse<SubmitResult>>> Upload(IFormFile file)
    {
        if (file is null || file.Length == 0)
            return new ApiResponse<SubmitResult> { Code = 1, Message = "File is required.", Result = new() };

        try
        {
            var fileName = Path.GetFileName(file.FileName);

            var code = await GenerateUniqueCodeAsync("file");
            if (code is null)
                return new ApiResponse<SubmitResult> { Code = 1, Message = "Unable to generate unique code, please retry.", Result = new() };

            await _kvService.SetAsync($"{code}_file", fileName);

            using var stream = file.OpenReadStream();
            await _blobService.UploadAsync($"file-{code}", stream);

            return new ApiResponse<SubmitResult> { Code = 0, Result = new SubmitResult { Code = code } };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Upload error");
            return new ApiResponse<SubmitResult> { Code = 1, Message = "Internal server error.", Result = new() };
        }
    }

    [HttpGet("checkfile/{code}")]
    public async Task<ActionResult<ApiResponse<CheckFileResult>>> CheckFile(string code)
    {
        try
        {
            if (string.IsNullOrEmpty(code))
                return new ApiResponse<CheckFileResult> { Code = 1, Message = "Code is missed.", Result = new() };

            var fileName = await _kvService.GetAsync($"{code}_file");
            if (fileName is null)
                return new ApiResponse<CheckFileResult> { Code = 2, Message = "Code does not exist.", Result = new() };

            return new ApiResponse<CheckFileResult> { Code = 0, Result = new CheckFileResult { Filename = fileName } };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Check file error");
            return new ApiResponse<CheckFileResult> { Code = 1, Message = "Internal server error.", Result = new() };
        }
    }

    [HttpGet("download/{code}")]
    public async Task<IActionResult> Download(string code)
    {
        if (string.IsNullOrEmpty(code))
            return BadRequest("Code is missed.");

        var fileName = await _kvService.GetAsync($"{code}_file");
        if (fileName is null)
            return NotFound("Code does not exist.");

        try
        {
            var stream = await _blobService.DownloadAsync($"file-{code}");
            return File(stream, MediaTypeNames.Application.Octet, fileName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Download error");
            return StatusCode(500, "Internal server error.");
        }
    }
}
