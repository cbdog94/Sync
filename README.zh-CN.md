# Sync - ASP.NET Core + Vue

中文 | [English](README.md)

文本和文件同步工具，使用 ASP.NET Core 后端 + Vue 3 前端。

## 项目结构

```
Sync/
├── Sync.Backend/          # ASP.NET Core Web API (.NET 10)
│   ├── Controllers/       # API 控制器
│   ├── Models/            # 数据模型和配置
│   ├── Services/          # Azure SQL / Blob 服务
│   ├── wwwroot/           # 前端构建输出 (build 后生成)
│   ├── Program.cs         # 应用入口
│   └── appsettings.json   # 配置文件
└── Sync.Frontend/         # Vue 3 + Vite + Element Plus
    ├── src/
    │   ├── api/           # API 调用封装
    │   ├── views/         # 页面组件
    │   ├── App.vue        # 根组件
    │   └── main.ts        # 入口文件
    ├── vite.config.ts     # Vite 配置
    └── package.json
```

## 开发

### 后端

```bash
cd Sync.Backend

# 配置 appsettings.json 中的 Azure 连接信息
# 运行
dotnet run
```

后端默认监听 `http://localhost:5000`。

### 前端

```bash
cd Sync.Frontend

# 安装依赖
pnpm install

# 开发模式 (自动代理到后端)
pnpm dev

# 构建 (输出到 Sync.Backend/wwwroot)
pnpm build
```

前端开发服务器在 `http://localhost:3000`，API 请求会自动代理到后端。

## Docker

无需 .NET SDK 或 Node.js，只需 Docker。

### Docker Compose（使用 Azure CLI 凭据的本地开发）

使用 [azure-cli-credentials-proxy](https://github.com/workleap/azure-cli-credentials-proxy)，让本地 `az login` 会话在容器内生效：

```bash
# 先登录 Azure
az login

# 启动所有服务
docker compose up --build
```

应用将在 `http://localhost:8080` 可用。

## 部署

1. 构建前端：`cd Sync.Frontend && pnpm build`
2. 发布后端：`cd Sync.Backend && dotnet publish -c Release`

前端构建产物会输出到 `Sync.Backend/wwwroot/`，后端会自动托管静态文件。
