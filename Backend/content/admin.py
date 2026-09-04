from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import BlogCategory, BlogTag, BlogPost, StaticPage

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'featured_image_preview', 'author', 'status', 'publish_date')
    list_filter = ('status', 'publish_date', 'categories')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('categories', 'tags', 'related_tours')

    def featured_image_preview(self, obj):
        if obj.featured_image:
            return mark_safe(f'<img src="{obj.featured_image.url}" style="height:40px; width:60px; object-fit:cover; border-radius:6px; border:1px solid #CBD5E1;">')
        return mark_safe('<span style="color:#94A3B8; font-size:0.8rem;">No image</span>')
    featured_image_preview.short_description = "Image"

@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
