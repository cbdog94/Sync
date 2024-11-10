import os
from io import BytesIO
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


container_name = "sync-files"
account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")

if account_url is None:
    print(
        "Please ensure environmnet variable AZURE_STORAGE_ACCOUNT_URL is set in current process."
    )
    exit(1)

default_credential = DefaultAzureCredential()
blob_service_client = BlobServiceClient(account_url, credential=default_credential)


def upload(file_name, file_data):
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=file_name
    )
    blob_client.upload_blob(file_data)


def download(file_name):
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=file_name
    )
    download_stream = BytesIO()
    blob_client.download_blob().readinto(download_stream)
    download_stream.seek(0)
    return download_stream
