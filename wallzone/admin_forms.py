# app/forms.py

from django import forms
from .models import Wallpaper
from PIL import Image, ImageSequence
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid
import boto3
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


def upload_to_s3(file_obj, path):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        s3.upload_fileobj(ContentFile(file_obj.read()), settings.AWS_STORAGE_BUCKET_NAME, path, ExtraArgs={'ContentType': file_obj.content_type})
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        raise e

def upload_to_storage(file_obj, path):
    print(file_obj.closed)
    file_obj.seek(0)
    if settings.USE_S3_STORAGE:
        upload_to_s3(file_obj, path)
    else:
        # Upload to local
        default_storage.save(path, ContentFile(file_obj.read()))

def generate_static_image_thumbnail(upload, size=(300, 300)):
    image = Image.open(upload)
    image.thumbnail(size)
    thumb_io = BytesIO()
    image_format = image.format or 'JPEG'
    content_type = f'image/{image_format.lower()}'

    image.save(thumb_io, format=image_format)
    thumb_io.seek(0)
    return InMemoryUploadedFile(
        thumb_io, None, upload.name, content_type, thumb_io.tell(), None
    )

def generate_gif_thumbnail(upload, size=(300, 560)):
    image = Image.open(upload)

    frames = []
    duration = image.info.get('duration', 100)
    loop = image.info.get('loop', 0)

    for frame in ImageSequence.Iterator(image):
        frame = frame.convert('RGBA')
        frame.thumbnail(size, Image.Resampling.LANCZOS)
        frames.append(frame)

    thumb_io = BytesIO()
    frames[0].save(
        thumb_io,
        format='GIF',
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop,
        disposal=2
    )
    thumb_io.seek(0)
    return InMemoryUploadedFile(
        thumb_io, None, upload.name, 'image/gif', thumb_io.tell(), None
    )

def generate_thumbnail(upload, size=(300, 560)):
    image = Image.open(upload)
    if image.format == 'GIF' and getattr(image, 'is_animated', False):
        return generate_gif_thumbnail(upload, size)
    return generate_static_image_thumbnail(upload, size)


# def generate_thumbnail(upload):
#     image = Image.open(upload)
#     image.thumbnail((300, 300))
#     thumb_io = BytesIO()
#     image.save(thumb_io, format=image.format)
#     thumb_io.seek(0)
#     return InMemoryUploadedFile(thumb_io, None, upload.name, upload.content_type, thumb_io.tell(), None)

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
