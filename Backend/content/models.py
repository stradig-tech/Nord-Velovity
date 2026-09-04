from django.db import models
from django.conf import settings
from tours.models import Tour

class BlogCategory(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class BlogTag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='blog_posts')
    
    featured_image = models.ImageField(upload_to='blog/')
    featured_image_alt = models.CharField(max_length=200, blank=True)
    
    excerpt = models.TextField(help_text="Short summary for listings")
    body = models.TextField(help_text="Rich text content")
    
    categories = models.ManyToManyField(BlogCategory, related_name='posts')
    tags = models.ManyToManyField(BlogTag, related_name='posts', blank=True)
    related_tours = models.ManyToManyField(Tour, related_name='blog_posts', blank=True)
    
    STATUS_CHOICES = (('DRAFT', 'Draft'), ('REVIEW', 'In Review'), ('PUBLISHED', 'Published'), ('SCHEDULED', 'Scheduled'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    publish_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class StaticPage(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField(help_text="Rich text")
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
