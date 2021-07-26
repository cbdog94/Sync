import os
from azure.storage.blob import BlobServiceClient
from io import BytesIO


container_name = "sync-files"
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

blob_service_client = BlobServiceClient.from_connection_string(connect_str)


def upload(file_name, file_data):
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=file_name)
    blob_client.upload_blob(file_data)


def download(file_name):
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=file_name)
    download_stream = BytesIO()
    blob_client.download_blob().readinto(download_stream)
    download_stream.seek(0)
    return download_stream
