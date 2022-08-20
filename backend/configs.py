import os

if os.getenv('AZURE_REDIS_HOST') is None:
    print('Please ensure environmnet variable AZURE_REDIS_HOST is set in current process.')
    exit(1)

if os.getenv('AZURE_REDIS_PASSWORD') is None:
    print('Please ensure environmnet variable AZURE_REDIS_PASSWORD is set in current process.')
    exit(1)

configs = {
    'redis': {
        'host': os.getenv('AZURE_REDIS_HOST'),
        'port': 6380,
        'db': 0,
        'password': os.getenv('AZURE_REDIS_PASSWORD'),
        'ssl': True,
        'decode_responses': True
    }
}
