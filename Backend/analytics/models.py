from django.db import models
from django.conf import settings

class PageView(models.Model):
    path = models.CharField(max_length=500)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.path} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class BookingFunnelEvent(models.Model):
    STAGE_CHOICES = (
        ('VIEW_DETAIL', 'View Detail'),
        ('SELECT_DATE', 'Select Date'),
        ('INITIATE_CHECKOUT', 'Initiate Checkout'),
        ('APPLY_COUPON', 'Apply Coupon'),
        ('PAYMENT_SUBMITTED', 'Payment Submitted'),
        ('BOOKING_CONFIRMED', 'Booking Confirmed'),
        ('BOOKING_ABANDONED', 'Booking Abandoned'),
    )
    stage = models.CharField(max_length=30, choices=STAGE_CHOICES)
    session_key = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    tour = models.ForeignKey('tours.Tour', on_delete=models.SET_NULL, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stage} ({self.session_key[:8]})"

class SearchQueryLog(models.Model):
    query = models.CharField(max_length=255)
    destination = models.ForeignKey('tours.Destination', on_delete=models.SET_NULL, null=True, blank=True)
    results_count = models.IntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Search: '{self.query}' ({self.results_count} results)"

