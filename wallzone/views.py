
from .models import Wallpaper
from .serializers import WallpaperSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.http import JsonResponse


class WallpaperDetailView(APIView):
    def get(self, request, slug):
        wallpaper = get_object_or_404(Wallpaper, slug=slug)
        serializer = WallpaperSerializer(wallpaper)
        return JsonResponse(serializer.data)
    
class WallpaperPagination(PageNumberPagination):
    page_size = 10  # Set the number of wallpapers per page
    page_size_query_param = 'page_size'
    max_page_size = 100
        
class WallpaperListView(APIView):
    def get(self, request):
        print("Request Headers:", request.query_params)
        queryset = Wallpaper.objects.filter(is_active=True).order_by('uploaded_at')
        queryset = queryset.prefetch_related('category', 'tags')
        
        category_ids = request.GET.getlist('category')
        if category_ids:
            queryset = queryset.filter(category__id__in=category_ids)
        
        tag_ids = request.GET.getlist('tags')
        if tag_ids:
            queryset = queryset.filter(tag__id__in=tag_ids)
        
        print(str(queryset.query))

        # Paginate the results
        paginator = WallpaperPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = WallpaperSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)