from django.contrib import admin
from .models import SEOMetadata, Redirect

@admin.register(SEOMetadata)
class SEOMetadataAdmin(admin.ModelAdmin):
    list_display = ('seo_title', 'content_type', 'object_id', 'updated_at')
    list_filter = ('content_type',)
    search_fields = ('seo_title', 'meta_description')

@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ('old_path', 'new_path', 'redirect_type', 'is_active', 'hit_count')
    list_filter = ('redirect_type', 'is_active')
    search_fields = ('old_path', 'new_path')
