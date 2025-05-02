# settings/media_storage.py

import os
from decouple import config

USE_S3_STORAGE = config('USE_S3_STORAGE', default=False, cast=bool)

if not USE_S3_STORAGE:
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
else:
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_QUERYSTRING_AUTH = False
    MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/'
