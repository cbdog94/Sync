FROM python:3.7-alpine
WORKDIR /sync_backend

COPY requirements.txt ./
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .
