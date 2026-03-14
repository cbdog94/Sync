using Sync.Backend.Models;
using Sync.Backend.Services;

var builder = WebApplication.CreateBuilder(args);

// Configuration
builder.Services.Configure<SyncSettings>(builder.Configuration.GetSection("Sync"));

// Service registration
builder.Services.AddSingleton<SqlService>();
builder.Services.AddSingleton<BlobService>();

// Controllers
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.PropertyNamingPolicy = System.Text.Json.JsonNamingPolicy.CamelCase;
    });

builder.Services.AddOpenApi();

// CORS (only needed in development; production serves frontend and backend from the same origin)
if (builder.Environment.IsDevelopment())
{
    builder.Services.AddCors(options =>
    {
        options.AddDefaultPolicy(policy =>
        {
            policy.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader();
        });
    });
}

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.UseCors();
}

// Static file serving (frontend)
var distPath = Path.Combine(app.Environment.ContentRootPath, "wwwroot");
if (Directory.Exists(distPath))
{
    app.UseDefaultFiles();
    app.UseStaticFiles();
}

app.MapControllers();

// SPA fallback - unmatched routes return index.html
if (Directory.Exists(distPath))
{
    app.MapFallbackToFile("index.html");
}

// Warm up SQL connection pool
await app.Services.GetRequiredService<SqlService>().WarmupAsync();

app.Run();
