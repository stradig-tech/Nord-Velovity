from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class SEOMetadata(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    seo_title = models.CharField(max_length=60)
    meta_description = models.CharField(max_length=160)
    canonical_url = models.URLField(blank=True, null=True)
    og_title = models.CharField(max_length=60, blank=True, null=True)
    og_description = models.TextField(blank=True, null=True)
    og_image = models.ImageField(upload_to='seo/', blank=True, null=True)
    robots_directive = models.CharField(max_length=50, default='index,follow')
    structured_data = models.JSONField(blank=True, null=True, help_text="JSON-LD markup")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('content_type', 'object_id')
        verbose_name_plural = "SEO Metadata"

class Redirect(models.Model):
    old_path = models.CharField(max_length=250, unique=True) # e.g. /old-tour/
    new_path = models.CharField(max_length=250)
    REDIRECT_CHOICES = (('PERMANENT_301', '301 Permanent'), ('TEMPORARY_302', '302 Temporary'))
    redirect_type = models.CharField(max_length=20, choices=REDIRECT_CHOICES, default='PERMANENT_301')
    is_active = models.BooleanField(default=True)
    hit_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
