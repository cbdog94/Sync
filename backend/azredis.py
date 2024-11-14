import base64
import json
import os
import redis
import time

from azure.identity import DefaultAzureCredential

host = os.getenv("AZURE_REDIS_HOST")

if host is None:
    print(
        "Please ensure environmnet variable AZURE_REDIS_HOST is set in current process."
    )
    exit(1)


def extract_username_from_token(token):
    parts = token.split(".")
    base64_str = parts[1]

    if len(base64_str) % 4 == 2:
        base64_str += "=="
    elif len(base64_str) % 4 == 3:
        base64_str += "="

    json_bytes = base64.b64decode(base64_str)
    json_str = json_bytes.decode("utf-8")
    jwt = json.loads(json_str)

    return jwt["oid"]


class AzureRedisClient:
    def __init__(self, host, scope="https://redis.azure.com/.default"):
        self.cred = DefaultAzureCredential()
        self.scope = scope
        self.token = self.cred.get_token(self.scope)
        self.user_name = extract_username_from_token(self.token.token)
        self.r = redis.Redis(
            host=host,
            port=6380,
            db=0,
            ssl=True,
            username=self.user_name,
            password=self.token.token,
            decode_responses=True,
        )

    def need_refreshing(self, refresh_offset=300):
        return not self.token or self.token.expires_on - time.time() < refresh_offset

    def refresh_token(self):
        if self.need_refreshing():
            print("Refreshing token...")
            self.token = self.cred.get_token(self.scope)
            self.r = redis.Redis(
                host=host,
                port=6380,
                db=0,
                ssl=True,
                username=self.user_name,
                password=self.token.token,
                decode_responses=True,
            )

    def get(self, key):
        self.refresh_token()
        return self.r.get(key)

    def delete(self, key):
        self.refresh_token()
        return self.r.delete(key)

    def set(self, key, value):
        self.refresh_token()
        self.r.set(key, value, ex=3600)


# Usage
azure_redis_client = AzureRedisClient(host)

def get(key):
    return azure_redis_client.get(key)

def delete(key):
    return azure_redis_client.delete(key)

def set(key, value):
    azure_redis_client.set(key, value)