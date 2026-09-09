from django.db import models


class Channel(models.Model):
    """Registered sales/distribution channel (e.g., GetYourGuide, Viator, Direct)."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    adapter_class = models.CharField(
        max_length=200, blank=True,
        help_text="Python dotted path to adapter, e.g. channels.adapters.gyg.GetYourGuideAdapter"
    )
    api_key = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    webhook_secret = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=False)
    sync_interval_minutes = models.PositiveIntegerField(default=15)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    last_sync_status = models.CharField(max_length=20, default='NEVER_RUN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "OTA Channel"
        verbose_name_plural = "OTA Channels"

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"


class ChannelSyncLog(models.Model):
    """Audit trail for every OTA sync attempt — successes AND failures."""
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='sync_logs')
    ACTION_CHOICES = (
        ('AVAILABILITY_PUSH', 'Availability Push'),
        ('BOOKING_IMPORT', 'Booking Import'),
        ('CANCELLATION_SYNC', 'Cancellation Sync'),
        ('WEBHOOK_RECEIVED', 'Webhook Received'),
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=(('SUCCESS', 'Success'), ('FAILED', 'Failed'), ('RETRYING', 'Retrying')),
        default='SUCCESS'
    )
    departure = models.ForeignKey(
        'tours.Departure', on_delete=models.SET_NULL, null=True, blank=True, related_name='sync_logs'
    )
    request_payload = models.JSONField(default=dict, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    requires_attention = models.BooleanField(
        default=False,
        help_text="True if this failure needs manual admin review or notification"
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Channel Sync Log"
        verbose_name_plural = "Channel Sync Logs"

    def __str__(self):
        return f"[{self.status}] {self.channel.name} - {self.get_action_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
