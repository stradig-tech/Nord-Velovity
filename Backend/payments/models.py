from django.db import models
from django.conf import settings

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True) # e.g. WINTER25
    TYPE_CHOICES = (('PERCENT', 'Percentage'), ('FIXED', 'Fixed Amount'))
    discount_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    max_uses = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)
    
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    APP_CHOICES = (('CHAUFFEUR', 'Chauffeur'), ('TOUR', 'Tour'), ('BOTH', 'Both'))
    applicable_to = models.CharField(max_length=10, choices=APP_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

class PaymentIntent(models.Model):
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='payments')
    stripe_payment_intent_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'), ('REQUIRES_ACTION', 'Requires Action'),
        ('SUCCEEDED', 'Succeeded'), ('FAILED', 'Failed'), ('CANCELLED', 'Cancelled')
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    payment_method_type = models.CharField(max_length=50) # card, wallet
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    idempotency_key = models.CharField(max_length=100, unique=True)
    stripe_metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Refund(models.Model):
    payment_intent = models.ForeignKey(PaymentIntent, on_delete=models.CASCADE, related_name='refunds')
    stripe_refund_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    
    STATUS_CHOICES = (('PENDING', 'Pending'), ('SUCCEEDED', 'Succeeded'), ('FAILED', 'Failed'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    initiated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='refunds_initiated')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, null=True, blank=True, related_name='refunds_approved')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Receipt(models.Model):
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='receipts')
    receipt_number = models.CharField(max_length=100, unique=True)
    pdf_file = models.FileField(upload_to='receipts/')
    generated_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, related_name='coupon_usages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='coupon_usages')
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.coupon.code} on {self.booking.booking_ref} (-€{self.discount_applied})"

