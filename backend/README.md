# 后端

基于 FastAPI + Azure SQL + Azure Blob Storage

## 技术栈

- **FastAPI** - 现代高性能 Python Web 框架
- **Pydantic** - 数据验证和设置管理
- **Uvicorn** - 高性能 ASGI 服务器
- **Azure SDK** - Azure 服务集成

## 环境要求

- Python >= 3.11
- Azure CLI (用于本地认证)

## 开始

```bash
# 进入 backend 目录
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 开发

```bash
# 登录 Azure（用于本地认证）
az login

# 设置环境变量
export AZURE_SQL_SERVER="your-server.database.windows.net"
export AZURE_SQL_DATABASE="your-database"
export AZURE_STORAGE_ACCOUNT_URL="https://your-account.blob.core.windows.net"

# 启动开发服务器（支持热重载）
uvicorn app.main:app --reload --port 8000
```

## API 文档

启动后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 部署

```bash
# 使用 Uvicorn 多进程
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 测试 API

```bash
# 健康检查
curl http://127.0.0.1:8000/syncbackend/health

# 同步文本
curl -X POST http://127.0.0.1:8000/syncbackend/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "once": true}'

# 提取文本
curl -X POST http://127.0.0.1:8000/syncbackend/extract \
  -H "Content-Type: application/json" \
  -d '{"code": "1234"}'
```

## 更新依赖

```bash
source .venv/bin/activate
pip install --upgrade -r requirements.txt
```

## 项目结构

```
backend/
├── app/
│   ├── routers/          # API 路由
│   │   └── api.py
│   ├── services/         # 业务服务
│   │   ├── sql_service.py
│   │   └── blob_service.py
│   ├── config.py         # 配置管理
│   ├── schemas.py        # Pydantic 模型
│   └── main.py           # FastAPI 应用入口
├── dist/                 # 前端构建产物
└── requirements.txt
```