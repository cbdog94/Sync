from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """通用 API 响应"""
    code: int = 0
    message: str = ""
    result: T


class SubmitRequest(BaseModel):
    """提交文本请求"""
    text: str = Field(..., min_length=1)
    once: bool = False


class SubmitResult(BaseModel):
    """提交文本结果"""
    code: str


class ExtractRequest(BaseModel):
    """提取文本请求"""
    code: str = Field(..., min_length=4, max_length=4)


class ExtractResult(BaseModel):
    """提取文本结果"""
    text: str = ""


class CheckFileResult(BaseModel):
    """检查文件结果"""
    filename: str = ""


class HealthResult(BaseModel):
    """健康检查结果"""
    pass
