import base64
import json
import os

from azure.identity import DefaultAzureCredential

if os.getenv('AZURE_REDIS_HOST') is None:
    print('Please ensure environmnet variable AZURE_REDIS_HOST is set in current process.')
    exit(1)

def extract_username_from_token(token):
    parts = token.split('.')
    base64_str = parts[1]

    if len(base64_str) % 4 == 2:
        base64_str += "=="
    elif len(base64_str) % 4 == 3:
        base64_str += "="

    json_bytes = base64.b64decode(base64_str)
    json_str = json_bytes.decode('utf-8')
    jwt = json.loads(json_str)

    return jwt['oid']

scope = "https://redis.azure.com/.default" 
cred = DefaultAzureCredential()
token = cred.get_token(scope)
user_name = extract_username_from_token(token.token)

configs = {
    'redis': {
        'host': os.getenv('AZURE_REDIS_HOST'),
        'port': 6380,
        'db': 0,
        'username': user_name,
        'password': token.token,
        'ssl': True,
        'decode_responses': True
    }
}
