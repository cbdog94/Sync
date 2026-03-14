namespace Sync.Backend.Models;

/// <summary>Generic API response</summary>
public class ApiResponse<T>
{
    public int Code { get; set; }
    public string Message { get; set; } = "";
    public T? Result { get; set; }
}

/// <summary>Submit text request</summary>
public class SubmitRequest
{
    public string Text { get; set; } = "";
    public bool Once { get; set; }
}

/// <summary>Submit/upload result</summary>
public class SubmitResult
{
    public string Code { get; set; } = "";
}

/// <summary>Extract text request</summary>
public class ExtractRequest
{
    public string Code { get; set; } = "";
}

/// <summary>Extract text result</summary>
public class ExtractResult
{
    public string Text { get; set; } = "";
}

/// <summary>Check file result</summary>
public class CheckFileResult
{
    public string Filename { get; set; } = "";
}

/// <summary>Health check result</summary>
public class HealthResult { }
