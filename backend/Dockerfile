FROM python:3.8
WORKDIR /sync_backend

COPY requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ENV AZURE_STORAGE_CONNECTION_STRING "Change to ABS connection string"

COPY . .
