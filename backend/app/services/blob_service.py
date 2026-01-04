"""Azure Blob Storage 服务"""
from io import BytesIO
from typing import BinaryIO

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from ..config import get_settings


class BlobService:
    """Azure Blob 存储服务"""
    
    def __init__(self):
        settings = get_settings()
        self.container_name = settings.azure_storage_container_name
        credential = DefaultAzureCredential()
        self.client = BlobServiceClient(
            settings.azure_storage_account_url,
            credential=credential
        )

    def upload(self, file_name: str, file_data: bytes):
        """上传文件"""
        blob_client = self.client.get_blob_client(
            container=self.container_name,
            blob=file_name
        )
        blob_client.upload_blob(file_data, overwrite=True)

    def download(self, file_name: str) -> BinaryIO:
        """下载文件"""
        blob_client = self.client.get_blob_client(
            container=self.container_name,
            blob=file_name
        )
        download_stream = BytesIO()
        blob_client.download_blob().readinto(download_stream)
        download_stream.seek(0)
        return download_stream


# 单例实例
blob_service = BlobService()
