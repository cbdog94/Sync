# Sync - 文本同步工具

一个简单的 Web 端文本同步工具。解决多平台下的文本同步痛点。

[DEMO](https://sync.cbdog94.com)

## 技术栈

### 前端
- **Vue 3** + **Composition API** + **TypeScript**
- **Vite** - 现代构建工具
- **Element Plus** - UI 组件库
- **VueUse** - 组合式 API 工具库

### 后端
- **FastAPI** - 现代异步 Web 框架
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI 服务器
- **Azure SQL** - 数据存储
- **Azure Blob Storage** - 文件存储

## 项目结构

```
Sync/
├── frontend/                # 前端项目
│   ├── src/
│   │   ├── api/            # API 服务
│   │   ├── views/          # 页面组件
│   │   ├── App.vue         # 根组件
│   │   └── main.ts         # 入口文件
│   ├── vite.config.ts      # Vite 配置
│   ├── tsconfig.json       # TypeScript 配置
│   └── package.json        # 依赖配置
│
└── backend/                 # 后端项目
    ├── app/
    │   ├── routers/        # API 路由
    │   ├── services/       # 业务服务
    │   ├── config.py       # 配置管理
    │   ├── schemas.py      # 数据模型
    │   └── main.py         # FastAPI 应用
    └── requirements.txt    # Python 依赖
```

## 快速开始

### 环境要求
- Node.js >= 18
- Python >= 3.11
- pnpm >= 9.0

### 前端开发

```bash
cd frontend

# 安装依赖
pnpm install

# 开发模式
pnpm dev

# 构建生产版本
pnpm build
```

### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export AZURE_SQL_SERVER="your-server.database.windows.net"
export AZURE_SQL_DATABASE="your-database"
export AZURE_STORAGE_ACCOUNT_URL="https://your-account.blob.core.windows.net"

# 开发模式运行
uvicorn app.main:app --reload --port 8000
```

## 部署

1. 构建前端：`cd frontend && yarn build`
2. 将 `frontend/dist` 复制到 `backend/dist`
3. 部署后端到 Azure App Service

## API 文档

启动后端后访问：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`