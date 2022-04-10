import os

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
