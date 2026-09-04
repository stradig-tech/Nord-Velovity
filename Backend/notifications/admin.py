from django.contrib import admin
from .models import NotificationTemplate, NotificationLog

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'channel', 'is_active')
    list_filter = ('channel', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'subject_template')

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('template', 'recipient_email', 'channel', 'status', 'sent_at')
    list_filter = ('status', 'channel', 'template')
    search_fields = ('recipient_email', 'booking__booking_ref')
    readonly_fields = ('sent_at', 'delivered_at')
