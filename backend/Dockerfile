FROM python:3.10
WORKDIR /sync_backend

COPY requirements.txt ./
RUN pip install -r requirements.txt

ENV AZURE_STORAGE_CONNECTION_STRING "Change to ABS connection string"
ENV AZURE_REDIS_HOST "Change to Azure Redis host name"
ENV AZURE_REDIS_PASSWORD "Change to Azure Redis password"

COPY . .

ENTRYPOINT [ "gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app" ]

EXPOSE 8000