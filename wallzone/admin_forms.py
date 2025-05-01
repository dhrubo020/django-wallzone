# app/forms.py

from django import forms
from .models import Wallpaper
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid
import boto3
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


def upload_to_s3(file_obj, path):
    # Upload to S3
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        s3.upload_fileobj(file_obj, settings.AWS_STORAGE_BUCKET_NAME, path)

def upload_to_storage(file_obj, path):
    file_obj.seek(0)
    if settings.USE_CLOUD_STORAGE:
        upload_to_s3(file_obj, path)
    else:
        # Upload to local
        default_storage.save(path, ContentFile(file_obj.read()))

def generate_thumbnail(upload):
    image = Image.open(upload)
    image.thumbnail((300, 300))
    thumb_io = BytesIO()
    image.save(thumb_io, format=image.format)
    return InMemoryUploadedFile(thumb_io, None, upload.name, upload.content_type, thumb_io.tell(), None)

class WallpaperAdminForm(forms.ModelForm):
    upload_image = forms.ImageField(required=False)

    class Meta:
        model = Wallpaper
        fields = ['title', 'slug', 'upload_image' , 'category', 'tags', 'is_active', 'original_file_key', 'thumbnail_file_key']

    def save(self, commit=True):
        instance = super().save(commit=False)
        upload = self.cleaned_data.get('upload_image')

        if upload:
            ext = upload.name.split('.')[-1]
            base_key = f"wallpapers/{uuid.uuid4()}"

            # Original
            original_key = f"{base_key}_original.{ext}"
            upload_to_storage(upload, original_key)
            instance.original_file_key = original_key

            # Thumbnail
            thumb = generate_thumbnail(upload)
            thumb_key = f"{base_key}_thumb.{ext}"
            upload_to_storage(thumb, thumb_key)
            instance.thumbnail_file_key = thumb_key

        if commit:
            instance.save()
        return instance
