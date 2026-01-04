from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # Azure SQL 配置
    azure_sql_server: str = ""
    azure_sql_database: str = ""
    
    # Azure Storage 配置
    azure_storage_account_url: str = ""
    azure_storage_container_name: str = "sync-files"
    
    # 应用配置
    api_prefix: str = "/syncbackend"
    dist_dir: str = "dist"
    text_expiry_seconds: int = 3600
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
