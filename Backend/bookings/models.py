from django.db import models
from django.conf import settings
from chauffeur.models import Vehicle
from tours.models import Tour, TourDate

class Booking(models.Model):
    booking_ref = models.CharField(max_length=50, unique=True) # e.g. NV-2026-00001
    TYPE_CHOICES = (('CHAUFFEUR', 'Chauffeur'), ('TOUR', 'Tour'))
    booking_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, related_name='bookings')
    coupon = models.ForeignKey('payments.Coupon', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    
    STATUS_CHOICES = (
        ('HELD', 'Held / Reserved'),
        ('PENDING', 'Pending'),
        ('PENDING_PAYMENT', 'Pending Payment'),
        ('CONFIRMED', 'Confirmed'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
        ('REFUNDED', 'Refunded'),
        ('PARTIALLY_REFUNDED', 'Partially Refunded'),
    )
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING')

    SOURCE_CHOICES = (
        ('DIRECT', 'Direct Website'),
        ('GETYOURGUIDE', 'GetYourGuide'),
        ('VIATOR', 'Viator'),
        ('MANUAL', 'Manual (Phone/Agent)'),
        ('HOTEL_AGENT', 'Hotel Agent'),
        ('OTHER_OTA', 'Other OTA'),
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='DIRECT')
    external_reference = models.CharField(max_length=200, blank=True, null=True, help_text="External OTA booking reference ID")
    hold_expires_at = models.DateTimeField(null=True, blank=True, help_text="If status is HELD, auto-expire and release capacity after this time")

    PAYMENT_METHOD_CHOICES = (
        ('STRIPE', 'Credit Card (Stripe)'),
        ('OFFLINE', 'Pay on Arrival / Cash to Chauffeur'),
        ('BANK_TRANSFER', 'Bank Wire Transfer (SEPA / IBAN)'),
        ('PAYPAL', 'PayPal')
    )
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='STRIPE')

    PAYMENT_STATUS_CHOICES = (
        ('UNPAID', 'Unpaid / Pending Collection'),
        ('PAID', 'Paid & Reconciled'),
        ('REFUNDED', 'Refunded')
    )
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='UNPAID')
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    
    customer_notes = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.booking_ref

class ChauffeurBooking(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='chauffeur_booking')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.RESTRICT)
    
    pickup_address = models.CharField(max_length=250)
    pickup_lat = models.DecimalField(max_digits=9, decimal_places=6)
    pickup_lng = models.DecimalField(max_digits=9, decimal_places=6)
    
    destination_address = models.CharField(max_length=250)
    destination_lat = models.DecimalField(max_digits=9, decimal_places=6)
    destination_lng = models.DecimalField(max_digits=9, decimal_places=6)
    
    pickup_datetime = models.DateTimeField()
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    estimated_duration_min = models.IntegerField()
    
    quote_id = models.CharField(max_length=100)
    ROUTE_CHOICES = (('DISTANCE', 'Distance-based'), ('FIXED', 'Fixed Route'), ('HOURLY', 'Hourly'))
    route_type = models.CharField(max_length=20, choices=ROUTE_CHOICES)
    
    passenger_count = models.IntegerField()
    luggage_count = models.IntegerField()
    special_requests = models.TextField(blank=True, null=True)
    
    is_return = models.BooleanField(default=False)
    return_pickup_address = models.CharField(max_length=250, blank=True, null=True)
    return_datetime = models.DateTimeField(blank=True, null=True)

class TourBooking(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='tour_booking')
    tour = models.ForeignKey(Tour, on_delete=models.RESTRICT)
    tour_date = models.ForeignKey(TourDate, on_delete=models.SET_NULL, null=True, blank=True)
    departure = models.ForeignKey('tours.Departure', on_delete=models.SET_NULL, null=True, blank=True, related_name='tour_bookings')
    departure_capacity = models.ForeignKey('tours.DepartureCapacity', on_delete=models.SET_NULL, null=True, blank=True, related_name='tour_bookings')
    vehicle_type = models.ForeignKey('tours.VehicleType', on_delete=models.SET_NULL, null=True, blank=True, related_name='tour_bookings')
    
    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)
    total_guests = models.IntegerField()
    
    special_requests = models.TextField(blank=True, null=True)
    dietary_requirements = models.TextField(blank=True, null=True)

class TourBookingGuest(models.Model):
    tour_booking = models.ForeignKey(TourBooking, on_delete=models.CASCADE, related_name='guests')
    full_name = models.CharField(max_length=150)
    GUEST_CHOICES = (('ADULT', 'Adult'), ('CHILD', 'Child'))
    guest_type = models.CharField(max_length=10, choices=GUEST_CHOICES)
    date_of_birth = models.DateField(blank=True, null=True)
    passport_number = models.CharField(max_length=100, blank=True, null=True)
    special_needs = models.TextField(blank=True, null=True)

class BookingStatusLog(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_logs')
    old_status = models.CharField(max_length=25)
    new_status = models.CharField(max_length=25)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class GuaranteedReattempt(models.Model):
    """
    Tracks re-attempt eligibility for guaranteed experience tours (e.g., Northern Lights).
    Links original failed booking to a re-attempt on next available departure.
    """
    original_booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='reattempt_from')
    original_departure = models.ForeignKey('tours.Departure', on_delete=models.CASCADE, related_name='reattempts_originating')

    reattempt_departure = models.ForeignKey(
        'tours.Departure', on_delete=models.SET_NULL, null=True, blank=True, related_name='reattempts_received'
    )
    reattempt_booking = models.ForeignKey(
        Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='reattempt_to'
    )

    guests_count = models.PositiveIntegerField()
    REASON_CHOICES = (
        ('WEATHER', 'Weather Conditions / Aurora Not Visible'),
        ('OPERATIONAL', 'Operational Issue'),
        ('OTHER', 'Other'),
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='WEATHER')

    STATUS_CHOICES = (
        ('ELIGIBLE', 'Eligible for Re-attempt'),
        ('REBOOKED', 'Rebooked to New Departure'),
        ('DECLINED', 'Customer Declined'),
        ('EXPIRED', 'Offer Expired'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ELIGIBLE')

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Guaranteed Re-attempt"
        verbose_name_plural = "Guaranteed Re-attempts"

    def __str__(self):
        return f"Re-attempt: {self.original_booking.booking_ref} → {self.reattempt_departure or 'Pending'}"

