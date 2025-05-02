
from rest_framework import serializers
from .models import Wallpaper, Category, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class WallpaperSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    class Meta:
        model = Wallpaper
        fields = ['title', 'slug', 'category', 'tags', 'location', 'image_base_url', 'original_file_key', 'thumbnail_file_key', 'uploaded_at']
