"""API 路由"""
import random
import time
import logging
from typing import Annotated

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from werkzeug.utils import secure_filename

from ..schemas import (
    ApiResponse,
    SubmitRequest,
    SubmitResult,
    ExtractRequest,
    ExtractResult,
    CheckFileResult,
    HealthResult,
)
from ..services import sql_service, blob_service
from ..config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


def generate_code() -> str:
    """生成 4 位随机码"""
    return "%04d" % random.randint(0, 9999)


@router.get("/health")
async def health() -> ApiResponse[HealthResult]:
    """健康检查"""
    return ApiResponse(
        code=0,
        message="App is running.",
        result=HealthResult()
    )


@router.post("/submit")
async def submit(request: SubmitRequest) -> ApiResponse[SubmitResult]:
    """提交文本"""
    start_time = time.time()
    
    try:
        # 生成唯一码
        random_code = generate_code()
        check_start = time.time()
        
        while sql_service.get(f"{random_code}_text") is not None:
            random_code = generate_code()
        
        check_time = time.time()
        logger.info(f"Code uniqueness check took {check_time - check_start:.4f}s")
        
        # 存储文本和标志
        set_start = time.time()
        sql_service.set_many({
            f"{random_code}_text": request.text,
            f"{random_code}_once": str(request.once)
        }, expiry_seconds=settings.text_expiry_seconds)
        
        set_time = time.time()
        logger.info(f"Storing data took {set_time - set_start:.4f}s")
        
        total_time = time.time() - start_time
        logger.info(f"Total request processing took {total_time:.4f}s")
        
        return ApiResponse(
            code=0,
            message="",
            result=SubmitResult(code=random_code)
        )
    
    except Exception as e:
        logger.error(f"Submit error: {e}")
        return ApiResponse(
            code=1,
            message=str(e),
            result=SubmitResult(code="")
        )


@router.post("/extract")
async def extract(request: ExtractRequest) -> ApiResponse[ExtractResult]:
    """提取文本"""
    try:
        code = request.code
        
        # 批量获取
        results = sql_service.get_many([f"{code}_text", f"{code}_once"])
        
        if f"{code}_text" not in results:
            return ApiResponse(
                code=2,
                message="Code does not exist.",
                result=ExtractResult()
            )
        
        text = results[f"{code}_text"]
        once = results.get(f"{code}_once")
        
        # 阅后即焚
        if once == "True":
            sql_service.delete_many([f"{code}_text", f"{code}_once"])
        
        return ApiResponse(
            code=0,
            message="",
            result=ExtractResult(text=text)
        )
    
    except Exception as e:
        logger.error(f"Extract error: {e}")
        return ApiResponse(
            code=1,
            message=str(e),
            result=ExtractResult()
        )


@router.post("/upload")
async def upload(file: Annotated[UploadFile, File()]) -> ApiResponse[SubmitResult]:
    """上传文件"""
    try:
        file_name = secure_filename(file.filename or "unknown")
        
        # 生成唯一码
        random_code = generate_code()
        while sql_service.get(f"{random_code}_file") is not None:
            random_code = generate_code()
        
        # 存储文件信息
        sql_service.set(f"{random_code}_file", file_name)
        
        # 上传到 Blob
        file_content = await file.read()
        blob_service.upload(f"file-{random_code}", file_content)
        
        return ApiResponse(
            code=0,
            message="",
            result=SubmitResult(code=random_code)
        )
    
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return ApiResponse(
            code=1,
            message=str(e),
            result=SubmitResult(code="")
        )


@router.get("/checkfile/{code}")
async def check_file(code: str) -> ApiResponse[CheckFileResult]:
    """检查文件是否存在"""
    try:
        if not code:
            return ApiResponse(
                code=1,
                message="Code is missed.",
                result=CheckFileResult()
            )
        
        file_name = sql_service.get(f"{code}_file")
        
        if file_name is None:
            return ApiResponse(
                code=2,
                message="Code does not exist.",
                result=CheckFileResult()
            )
        
        return ApiResponse(
            code=0,
            message="",
            result=CheckFileResult(filename=file_name)
        )
    
    except Exception as e:
        logger.error(f"Check file error: {e}")
        return ApiResponse(
            code=1,
            message=str(e),
            result=CheckFileResult()
        )


@router.get("/download/{code}")
async def download(code: str):
    """下载文件"""
    if not code:
        raise HTTPException(status_code=400, detail="Code is missed.")
    
    file_name = sql_service.get(f"{code}_file")
    
    if file_name is None:
        raise HTTPException(status_code=404, detail="Code does not exist.")
    
    try:
        download_file = blob_service.download(f"file-{code}")
        
        return StreamingResponse(
            download_file,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{file_name}"'
            }
        )
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
