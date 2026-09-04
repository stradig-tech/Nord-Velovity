from django.db import models
from django.conf import settings

class NotificationTemplate(models.Model):
    name = models.CharField(max_length=150) # e.g. booking_confirmed
    slug = models.SlugField(unique=True)
    subject_template = models.CharField(max_length=250)
    body_html = models.TextField()
    body_text = models.TextField()
    CHANNEL_CHOICES = (('EMAIL', 'Email'), ('SMS', 'SMS'))
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default='EMAIL')
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class NotificationLog(models.Model):
    booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.RESTRICT)
    recipient_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    recipient_email = models.EmailField()
    recipient_phone = models.CharField(max_length=50, blank=True, null=True)
    
    CHANNEL_CHOICES = (('EMAIL', 'Email'), ('SMS', 'SMS'))
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    
    STATUS_CHOICES = (
        ('QUEUED', 'Queued'), ('SENT', 'Sent'), ('DELIVERED', 'Delivered'),
        ('FAILED', 'Failed'), ('BOUNCED', 'Bounced')
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='QUEUED')
    provider_message_id = models.CharField(max_length=250, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
