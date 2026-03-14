# Sync - ASP.NET Core + Vue

[中文](README.zh-CN.md) | English

A text and file sync tool built with ASP.NET Core backend + Vue 3 frontend.

## Project Structure

```
Sync/
├── Sync.Backend/          # ASP.NET Core Web API (.NET 10)
│   ├── Controllers/       # API controllers
│   ├── Models/            # Data models and settings
│   ├── Services/          # Azure SQL / Blob services
│   ├── wwwroot/           # Frontend build output (generated after build)
│   ├── Program.cs         # Application entry point
│   └── appsettings.json   # Configuration file
└── Sync.Frontend/         # Vue 3 + Vite + Element Plus
    ├── src/
    │   ├── api/           # API client
    │   ├── views/         # Page components
    │   ├── App.vue        # Root component
    │   └── main.ts        # Entry file
    ├── vite.config.ts     # Vite configuration
    └── package.json
```

## Development

### Backend

```bash
cd Sync.Backend

# Configure Azure connection info in appsettings.json
# Run
dotnet run
```

Backend listens on `http://localhost:5000` by default.

### Frontend

```bash
cd Sync.Frontend

# Install dependencies
pnpm install

# Development mode (auto-proxy to backend)
pnpm dev

# Build (output to Sync.Backend/wwwroot)
pnpm build
```

Frontend dev server runs at `http://localhost:3000`, API requests are automatically proxied to the backend.

## Docker

No .NET SDK or Node.js required — just Docker.

### Docker Compose (local development with Azure CLI credentials)

Uses [azure-cli-credentials-proxy](https://github.com/workleap/azure-cli-credentials-proxy) so your local `az login` session works inside containers:

```bash
# Login to Azure first
az login

# Start all services
docker compose up --build
```

The app will be available at `http://localhost:8080`.

## Deployment

1. Build frontend: `cd Sync.Frontend && pnpm build`
2. Publish backend: `cd Sync.Backend && dotnet publish -c Release`

Frontend build output goes to `Sync.Backend/wwwroot/`, the backend serves static files automatically.