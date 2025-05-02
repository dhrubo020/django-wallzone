from django.db import models
from django.utils.timezone import now
from django.utils.text import slugify
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(blank=True, upload_to='categories/')

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Wallpaper(models.Model):
    LOCATION_LOCAL = 1
    LOCATION_S3 = 2
    LOCATION_OTHER = 3

    LOCATION_CHOICES = [
        (LOCATION_LOCAL, 'Local'),
        (LOCATION_S3, 'S3'),
        (LOCATION_OTHER, 'Other'),
    ]
    location = models.IntegerField(choices=LOCATION_CHOICES, default=1)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    original_file_key = models.CharField(max_length=255, blank=True, null=True)
    thumbnail_file_key = models.CharField(max_length=255, blank=True, null=True)
    category = models.ManyToManyField('Category', related_name='wallpapers')
    tags = models.ManyToManyField('Tag', blank=True, related_name='wallpapers')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            similar = Wallpaper.objects.filter(slug__startswith=base_slug).count()
            self.slug = f"{base_slug}-{similar + 1}" if similar else base_slug
            
        if settings.USE_S3_STORAGE:
            self.location = self.LOCATION_S3
        else:
            self.location = self.LOCATION_LOCAL
            
        super().save(*args, **kwargs)

    @property
    def image_base_url(self):
        return f"{settings.IMAGE_BASE_URL}"
    
    def __str__(self):
        return self.title
    
class WallpaperView(models.Model):
    wallpaper = models.ForeignKey(Wallpaper, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(default=now)
    
    class Meta:
        ordering = ['-viewed_at']
