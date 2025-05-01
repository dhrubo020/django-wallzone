# settings/media_storage.py

import os
from decouple import config

USE_CLOUD_STORAGE = config('USE_CLOUD_STORAGE', default=False, cast=bool)

if not USE_CLOUD_STORAGE:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
else:
    INSTALLED_APPS = ['storages']

    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_QUERYSTRING_AUTH = False

    AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default=None)
    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
    else:
        MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/'
