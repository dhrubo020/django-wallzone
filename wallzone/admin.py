from django.contrib import admin
from django.utils.html import format_html
from .models import Wallpaper, Category, Tag
from .admin_forms import WallpaperAdminForm
from django.conf import settings

@admin.register(Wallpaper)
class WallpaperAdmin(admin.ModelAdmin):
    form = WallpaperAdminForm
    list_display = (
        'title',
        'slug',
        'location',
        'original_file_key',
        'thumbnail_file_key',
        'get_categories',
        'uploaded_at',
        'is_active'
    )
    search_fields = ('title', 'slug')
    list_filter = ('is_active', 'tags','category','location')  # Can't filter directly on M2M category

    

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.category.all()])
    get_categories.short_description = 'Categories'

    readonly_fields = ['preview_thumb','location']

    def preview_thumb(self, obj):
        if obj.thumbnail_file_key:
            # Generate the URL for the thumbnail image
            thumb_url = f"{settings.IMAGE_BASE_URL}{obj.thumbnail_file_key}"
            return format_html('<img src="{}" style="max-height: 100px;" />', thumb_url)
        return "No Thumbnail"
    preview_thumb.short_description = "Thumbnail"

admin.site.register(Category)
admin.site.register(Tag)
