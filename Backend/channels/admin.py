from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Channel, ChannelSyncLog
from .services import ChannelSyncService


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'last_sync_at', 'last_sync_status', 'sync_interval_minutes')
    list_editable = ('is_active', 'sync_interval_minutes')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    actions = ['activate_channel', 'deactivate_channel']

    @admin.action(description="✓ Activate selected channels")
    def activate_channel(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected channels activated.")

    @admin.action(description="✗ Deactivate selected channels")
    def deactivate_channel(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected channels deactivated.")


@admin.register(ChannelSyncLog)
class ChannelSyncLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'channel', 'action', 'status_badge', 'departure', 'requires_attention_badge', 'retry_count')
    list_filter = ('requires_attention', 'status', 'action', 'channel', 'created_at')
    search_fields = ('error_message', 'channel__name')
    readonly_fields = ('created_at', 'channel', 'action', 'status', 'departure', 'request_payload', 'response_payload', 'error_message', 'retry_count')
    date_hierarchy = 'created_at'
    actions = ['mark_as_resolved', 'retry_selected_syncs']

    def status_badge(self, obj):
        color = '#10B981' if obj.status == 'SUCCESS' else '#EF4444'
        return mark_safe(f'<span style="color:{color}; font-weight:700;">{obj.status}</span>')
    status_badge.short_description = "Status"

    def requires_attention_badge(self, obj):
        if obj.requires_attention:
            return mark_safe('<span style="background:#FEE2E2; color:#DC2626; padding:2px 8px; border-radius:4px; font-weight:700; font-size:0.75rem;">⚠️ ATTENTION NEEDED</span>')
        return mark_safe('<span style="color:#94A3B8; font-size:0.8rem;">Resolved / OK</span>')
    requires_attention_badge.short_description = "Attention"

    @admin.action(description="✓ Mark selected sync failures as Resolved")
    def mark_as_resolved(self, request, queryset):
        queryset.update(requires_attention=False, resolved_at=timezone.now())
        self.message_user(request, f"{queryset.count()} log(s) marked as resolved.")

    @admin.action(description="🔄 Retry selected syncs")
    def retry_selected_syncs(self, request, queryset):
        count = 0
        for log in queryset.filter(departure__isnull=False):
            ChannelSyncService.push_departure_availability(log.departure)
            log.retry_count += 1
            log.requires_attention = False
            log.resolved_at = timezone.now()
            log.save(update_fields=['retry_count', 'requires_attention', 'resolved_at'])
            count += 1
        self.message_user(request, f"{count} sync(s) re-dispatched.")
