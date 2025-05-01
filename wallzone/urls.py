from django.urls import path
from . import views

from django.urls import path
from .views import WallpaperListView, WallpaperDetailView

urlpatterns = [
    path('wallpapers/<slug:slug>/', WallpaperDetailView.as_view(), name='wallpaper-detail'),
    path('wallpapers/', WallpaperListView.as_view(), name='wallpaper-list'),
]