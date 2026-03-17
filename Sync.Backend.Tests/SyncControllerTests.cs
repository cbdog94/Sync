using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging.Abstractions;
using Microsoft.Extensions.Options;
using Sync.Backend.Controllers;
using Sync.Backend.Models;
using Sync.Backend.Services;

namespace Sync.Backend.Tests;

public class SyncControllerSubmitTests
{
    private readonly InMemoryKvService _kvService = new();
    private readonly SyncSettings _settings = new() { TextExpirySeconds = 3600 };

    private SyncController CreateController() =>
        new(_kvService, null!, Options.Create(_settings), NullLogger<SyncController>.Instance);

    [Fact]
    public async Task Submit_EmptyText_ReturnsError()
    {
        var controller = CreateController();
        var result = await controller.Submit(new SubmitRequest { Text = "" });

        var response = Assert.IsType<ApiResponse<SubmitResult>>(result.Value);
        Assert.Equal(1, response.Code);
        Assert.Equal("Text is required.", response.Message);
    }

    [Fact]
    public async Task Submit_WhitespaceText_ReturnsError()
    {
        var controller = CreateController();
        var result = await controller.Submit(new SubmitRequest { Text = "   " });

        var response = Assert.IsType<ApiResponse<SubmitResult>>(result.Value);
        Assert.Equal(1, response.Code);
    }

    [Fact]
    public async Task Submit_ValidText_ReturnsCodeAndStoresData()
    {
        var controller = CreateController();
        var result = await controller.Submit(new SubmitRequest { Text = "hello", Once = false });

        var response = Assert.IsType<ApiResponse<SubmitResult>>(result.Value);
        Assert.Equal(0, response.Code);
        Assert.NotNull(response.Result);
        Assert.Equal(4, response.Result!.Code.Length);

        // Verify data stored
        var code = response.Result.Code;
        var text = await _kvService.GetAsync($"{code}_text");
        Assert.Equal("hello", text);
        var once = await _kvService.GetAsync($"{code}_once");
        Assert.Equal("0", once);
    }

    [Fact]
    public async Task Submit_OnceTrue_StoresOnceFlag()
    {
        var controller = CreateController();
        var result = await controller.Submit(new SubmitRequest { Text = "secret", Once = true });

        var response = Assert.IsType<ApiResponse<SubmitResult>>(result.Value);
        Assert.Equal(0, response.Code);

        var code = response.Result!.Code;
        var once = await _kvService.GetAsync($"{code}_once");
        Assert.Equal("1", once);
    }
}

public class SyncControllerExtractTests
{
    private readonly InMemoryKvService _kvService = new();
    private readonly SyncSettings _settings = new() { TextExpirySeconds = 3600 };

    private SyncController CreateController() =>
        new(_kvService, null!, Options.Create(_settings), NullLogger<SyncController>.Instance);

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("abc")]
    [InlineData("12345")]
    public async Task Extract_InvalidCode_ReturnsError(string code)
    {
        var controller = CreateController();
        var result = await controller.Extract(new ExtractRequest { Code = code });

        var response = Assert.IsType<ApiResponse<ExtractResult>>(result.Value);
        Assert.Equal(1, response.Code);
        Assert.Equal("Invalid code.", response.Message);
    }

    [Fact]
    public async Task Extract_NonexistentCode_ReturnsCodeNotExist()
    {
        var controller = CreateController();
        var result = await controller.Extract(new ExtractRequest { Code = "9999" });

        var response = Assert.IsType<ApiResponse<ExtractResult>>(result.Value);
        Assert.Equal(2, response.Code);
        Assert.Equal("Code does not exist.", response.Message);
    }

    [Fact]
    public async Task Extract_ValidCode_ReturnsText()
    {
        await _kvService.SetManyAsync(new Dictionary<string, string>
        {
            ["1234_text"] = "hello world",
            ["1234_once"] = "0"
        });

        var controller = CreateController();
        var result = await controller.Extract(new ExtractRequest { Code = "1234" });

        var response = Assert.IsType<ApiResponse<ExtractResult>>(result.Value);
        Assert.Equal(0, response.Code);
        Assert.Equal("hello world", response.Result!.Text);

        // Data should still exist (once = 0)
        var text = await _kvService.GetAsync("1234_text");
        Assert.Equal("hello world", text);
    }

    [Fact]
    public async Task Extract_OnceCode_DeletesAfterExtract()
    {
        await _kvService.SetManyAsync(new Dictionary<string, string>
        {
            ["5678_text"] = "one-time secret",
            ["5678_once"] = "1"
        });

        var controller = CreateController();
        var result = await controller.Extract(new ExtractRequest { Code = "5678" });

        var response = Assert.IsType<ApiResponse<ExtractResult>>(result.Value);
        Assert.Equal(0, response.Code);
        Assert.Equal("one-time secret", response.Result!.Text);

        // Data should be deleted
        var text = await _kvService.GetAsync("5678_text");
        Assert.Null(text);
        var once = await _kvService.GetAsync("5678_once");
        Assert.Null(once);
    }

    [Fact]
    public async Task SubmitThenExtract_RoundTrip()
    {
        var controller = CreateController();

        var submitResult = await controller.Submit(new SubmitRequest { Text = "roundtrip test", Once = false });
        var submitResponse = Assert.IsType<ApiResponse<SubmitResult>>(submitResult.Value);
        var code = submitResponse.Result!.Code;

        var extractResult = await controller.Extract(new ExtractRequest { Code = code });
        var extractResponse = Assert.IsType<ApiResponse<ExtractResult>>(extractResult.Value);
        Assert.Equal(0, extractResponse.Code);
        Assert.Equal("roundtrip test", extractResponse.Result!.Text);
    }

    [Fact]
    public async Task SubmitOnceThenExtractTwice_SecondExtractFails()
    {
        var controller = CreateController();

        var submitResult = await controller.Submit(new SubmitRequest { Text = "once only", Once = true });
        var code = Assert.IsType<ApiResponse<SubmitResult>>(submitResult.Value).Result!.Code;

        // First extract succeeds
        var first = await controller.Extract(new ExtractRequest { Code = code });
        Assert.Equal(0, Assert.IsType<ApiResponse<ExtractResult>>(first.Value).Code);

        // Second extract fails
        var second = await controller.Extract(new ExtractRequest { Code = code });
        Assert.Equal(2, Assert.IsType<ApiResponse<ExtractResult>>(second.Value).Code);
    }
}
