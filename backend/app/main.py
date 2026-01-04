"""Sync App - FastAPI 应用"""
import os
import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import api_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

settings = get_settings()

app = FastAPI(
    title="Sync API",
    description="文本和文件同步工具 API",
    version="2.0.0",
)

# CORS 配置 (开发环境)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由
app.include_router(api_router, prefix=settings.api_prefix)

# 静态文件目录
APP_DIR = os.path.dirname(__file__)
DIST_DIR = os.path.join(os.path.dirname(APP_DIR), settings.dist_dir)


# 根路由返回前端页面
@app.get("/")
async def root():
    index_file = os.path.join(DIST_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Sync API is running. Frontend not deployed."}


# 静态文件服务
if os.path.exists(DIST_DIR):
    app.mount("/", StaticFiles(directory=DIST_DIR, html=True), name="static")
