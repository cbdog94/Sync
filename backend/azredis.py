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


scope = "https://redis.azure.com/.default"
cred = DefaultAzureCredential()
token = cred.get_token(scope)
user_name = extract_username_from_token(token.token)
r = redis.Redis(
    host=host,
    port=6380,
    db=0,
    ssl=True,
    username=user_name,
    password=token.token,
    decode_responses=True,
)


def need_refreshing(token, refresh_offset=300):
    return not token or token.expires_on - time.time() < refresh_offset


def get(key):
    global token
    if need_refreshing(token):
        print("Refreshing token...")
        tmp_token = cred.get_token(scope)
        if tmp_token:
            token = tmp_token
        r.execute_command("AUTH", user_name, token.token)
    return r.get(key)


def delete(key):
    global token
    if need_refreshing(token):
        print("Refreshing token...")
        tmp_token = cred.get_token(scope)
        if tmp_token:
            token = tmp_token
        r.execute_command("AUTH", user_name, token.token)
    return r.delete(key)


def set(key, value):
    global token
    if need_refreshing(token):
        print("Refreshing token...")
        tmp_token = cred.get_token(scope)
        if tmp_token:
            token = tmp_token
        r.execute_command("AUTH", user_name, token.token)
    r.set(key, value, ex=3600)