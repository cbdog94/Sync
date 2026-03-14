# Stage 1: Build frontend
FROM node:22-alpine AS frontend-build
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /src/Sync.Frontend
COPY Sync.Frontend/package.json Sync.Frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY Sync.Frontend/ ./
RUN pnpm build

# Stage 2: Build backend
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS backend-build
WORKDIR /src/Sync.Backend
COPY Sync.Backend/Sync.Backend.csproj ./
RUN dotnet restore
COPY Sync.Backend/ ./
COPY --from=frontend-build /src/Sync.Backend/wwwroot ./wwwroot
RUN dotnet publish -c Release -o /app

# Stage 3: Runtime
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
COPY --from=backend-build /app ./
EXPOSE 8080
ENTRYPOINT ["dotnet", "Sync.Backend.dll"]
