from django.db import models
from django.conf import settings
from chauffeur.models import Vehicle
from tours.models import Tour, TourDate, TourPickup

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
    is_free_booking = models.BooleanField(
        default=False,
        help_text="If True, this is a free booking — no payment required, info collection only"
    )
    
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
    
    pickup_location = models.ForeignKey(
        TourPickup, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='tour_bookings',
        help_text="Selected pickup point for this booking"
    )
    pickup_notes = models.TextField(blank=True, default='', help_text="Customer's pickup instructions or hotel name")
    
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

class GuestInfo(TourBookingGuest):
    """Proxy model to expose /admin/bookings/guestinfo/ for admin navigation."""
    class Meta:
        proxy = True
        verbose_name = "Guest Info"
        verbose_name_plural = "Guest Info"


class ChildSeatRequest(models.Model):
    """Child seat request for chauffeur or tour bookings."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='child_seat_requests')
    SEAT_TYPE_CHOICES = (
        ('INFANT', 'Infant Carrier (0-12 months)'),
        ('TODDLER', 'Toddler Seat (1-4 years)'),
        ('CHILD', 'Child Seat (4-7 years)'),
        ('BOOSTER', 'Booster Seat (7-12 years)'),
    )
    seat_type = models.CharField(max_length=10, choices=SEAT_TYPE_CHOICES)
    quantity = models.PositiveIntegerField(default=1)
    child_age = models.PositiveIntegerField(help_text="Child's age in years")
    approx_weight_kg = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True,
        help_text="Approximate weight in kg"
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Child Seat Request"
        verbose_name_plural = "Child Seat Requests"

    def __str__(self):
        return f"{self.get_seat_type_display()} x{self.quantity} (Age: {self.child_age})"


class BookingAnswer(models.Model):
    """Customer's answer to a per-tour BookingQuestion."""
    tour_booking = models.ForeignKey(TourBooking, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(
        'tours.BookingQuestion', on_delete=models.CASCADE, related_name='answers'
    )
    answer_text = models.TextField(blank=True)

    class Meta:
        unique_together = ('tour_booking', 'question')
        verbose_name = "Booking Answer"
        verbose_name_plural = "Booking Answers"

    def __str__(self):
        return f"{self.question.question_text}: {self.answer_text[:80]}"


class BookingAddon(models.Model):
    """Records which add-ons (TourExtraService) were selected for a booking."""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='addons')
    extra_service = models.ForeignKey(
        'tours.TourExtraService', on_delete=models.SET_NULL, null=True, related_name='booking_addons'
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Booking Add-on"
        verbose_name_plural = "Booking Add-ons"

    def __str__(self):
        name = self.extra_service.name if self.extra_service else "Deleted Add-on"
        return f"{name} x{self.quantity} (€{self.total_price})"



class BookingStatusLog(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_logs')
    old_status = models.CharField(max_length=25)
    new_status = models.CharField(max_length=25)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    reason = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class GuaranteedReattempt(models.Model):
    """
    DEPRECATED — Kept for migration compatibility only.
    Use GuaranteeOutcome + GuaranteePolicy for all new guarantee logic.
    """
    original_booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='reattempt_from')
    original_departure = models.ForeignKey(
        'tours.Departure', on_delete=models.SET_NULL, null=True, blank=True, related_name='reattempts_originating'
    )

    reattempt_departure = models.ForeignKey(
        'tours.Departure', on_delete=models.SET_NULL, null=True, blank=True, related_name='reattempts_received'
    )
    reattempt_booking = models.ForeignKey(
        Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='reattempt_to'
    )

    guests_count = models.PositiveIntegerField(default=1, blank=True, help_text="Defaults to booking guest count or 1 if left blank")
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
        verbose_name = "Guaranteed Re-attempt (Legacy)"
        verbose_name_plural = "Guaranteed Re-attempts (Legacy)"

    def clean(self):
        super().clean()
        if self.original_booking_id and not self.original_departure_id:
            if hasattr(self.original_booking, 'tour_booking') and self.original_booking.tour_booking.departure:
                self.original_departure = self.original_booking.tour_booking.departure
            elif hasattr(self.original_booking, 'tour_booking') and self.original_booking.tour_booking.tour:
                self.original_departure = self.original_booking.tour_booking.tour.departures.first()
        if not self.guests_count:
            if hasattr(self.original_booking, 'tour_booking') and self.original_booking.tour_booking.total_guests:
                self.guests_count = self.original_booking.tour_booking.total_guests
            else:
                self.guests_count = 1

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        ref = self.original_booking.booking_ref if self.original_booking_id else "Unknown"
        dep = self.reattempt_departure or "Pending"
        return f"Re-attempt: {ref} -> {dep}"



# =============================================================================
# NEW GUARANTEE SYSTEM — Admin-Configurable Policies + Full Lifecycle
# =============================================================================

class GuaranteePolicy(models.Model):
    """
    Admin-configurable guarantee policy that can be assigned to any tour/package.
    Different Aurora packages (or any future guaranteed experience) can use
    different policies independently.

    Policy parameters are NOT hard-coded — they are editable from the admin panel.
    Nord Velocity can introduce new guarantee products or modify policies at any time.
    """
    name = models.CharField(max_length=200, help_text="e.g. Northern Lights Standard Guarantee, Aurora Premium Guarantee")
    slug = models.SlugField(unique=True)

    GUARANTEE_TYPE_CHOICES = (
        ('REATTEMPT_ONLY', 'Re-attempt Only (no refund)'),
        ('REFUND_ONLY', 'Refund Only (no re-attempt)'),
        ('REATTEMPT_THEN_REFUND', 'Re-attempt first, then Refund if re-attempts exhausted'),
    )
    guarantee_type = models.CharField(
        max_length=30, choices=GUARANTEE_TYPE_CHOICES, default='REATTEMPT_THEN_REFUND',
        help_text="Determines the guarantee workflow: re-attempt, refund, or both"
    )

    # Re-attempt rules
    max_reattempts = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of re-attempt opportunities permitted under this policy"
    )
    reattempt_window_days = models.PositiveIntegerField(
        default=7,
        help_text="Number of days after the original tour within which a re-attempt must be scheduled"
    )

    # Refund rules
    refund_eligible = models.BooleanField(
        default=True,
        help_text="Whether this policy allows refund eligibility (after re-attempts exhausted, if applicable)"
    )
    refund_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=100.00,
        help_text="Percentage of original booking amount eligible for refund (e.g. 100 for full, 50 for half)"
    )
    refund_review_required = models.BooleanField(
        default=True,
        help_text="If True, admin must manually review and approve refund before processing"
    )

    # Customer-facing info
    description = models.TextField(
        blank=True,
        help_text="Customer-facing explanation of the guarantee (shown on tour detail page)"
    )
    terms_and_conditions = models.TextField(
        blank=True,
        help_text="Full terms and conditions for this guarantee policy"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Guarantee Policy"
        verbose_name_plural = "Guarantee Policies"

    def __str__(self):
        return f"{self.name} ({self.get_guarantee_type_display()})"


class GuaranteeOutcome(models.Model):
    """
    Tracks the full post-tour guarantee lifecycle per booking.

    Lifecycle Flow:
        Tour Completed → Aurora Result (Successful / Unsuccessful)
            → Re-attempt Eligible → Re-attempt Scheduled → Re-attempt Completed
            OR → Refund Eligibility Review → Refund Approved → Refund Processing → Refunded
            OR → Closed (if successful or customer declined)

    Admin maintains a full audit trail via GuaranteeAuditLog.
    """
    # Core references
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name='guarantee_outcomes',
        help_text="Original booking this guarantee outcome is for"
    )
    tour = models.ForeignKey(
        'tours.Tour', on_delete=models.CASCADE, related_name='guarantee_outcomes'
    )
    policy = models.ForeignKey(
        GuaranteePolicy, on_delete=models.PROTECT, related_name='outcomes',
        help_text="The guarantee policy that was applied (snapshot at time of outcome creation)"
    )
    departure = models.ForeignKey(
        'tours.Departure', on_delete=models.CASCADE, related_name='guarantee_outcomes',
        help_text="Original departure the customer attended"
    )
    guests_count = models.PositiveIntegerField(
        help_text="Number of guests covered by this guarantee"
    )

    # Aurora / Experience Result
    RESULT_CHOICES = (
        ('PENDING', 'Result Pending'),
        ('SUCCESSFUL', 'Successful'),
        ('UNSUCCESSFUL', 'Unsuccessful'),
    )
    aurora_result = models.CharField(
        max_length=20, choices=RESULT_CHOICES, default='PENDING',
        help_text="The outcome of the tour experience (e.g. Aurora visible = Successful)"
    )
    result_recorded_at = models.DateTimeField(null=True, blank=True)
    result_recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='guarantee_results_recorded'
    )
    result_notes = models.TextField(blank=True, help_text="Staff notes about the experience result")

    # Re-attempt tracking
    REASON_CHOICES = (
        ('WEATHER', 'Weather Conditions / Aurora Not Visible'),
        ('OPERATIONAL', 'Operational Issue'),
        ('SAFETY', 'Safety Conditions'),
        ('OTHER', 'Other Reason'),
    )
    unsuccessful_reason = models.CharField(
        max_length=20, choices=REASON_CHOICES, blank=True,
        help_text="Reason why the experience was unsuccessful"
    )
    reattempt_count = models.PositiveIntegerField(
        default=0, help_text="How many re-attempts have been used so far"
    )
    reattempt_departure = models.ForeignKey(
        'tours.Departure', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='guarantee_reattempts_received',
        help_text="Departure scheduled for re-attempt"
    )
    reattempt_booking = models.ForeignKey(
        Booking, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='guarantee_reattempt_bookings',
        help_text="New booking created for the re-attempt"
    )

    # Refund tracking
    REFUND_STATUS_CHOICES = (
        ('NONE', 'Not Applicable'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('PROCESSING', 'Processing'),
        ('REFUNDED', 'Refunded'),
        ('DENIED', 'Denied'),
    )
    refund_status = models.CharField(
        max_length=20, choices=REFUND_STATUS_CHOICES, default='NONE'
    )
    refund_eligible = models.BooleanField(
        default=False, help_text="Whether this outcome qualifies for refund under the policy"
    )
    refund_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Calculated refund amount based on policy percentage"
    )
    refund = models.ForeignKey(
        'payments.Refund', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='guarantee_outcomes',
        help_text="Link to the actual payment refund record"
    )
    refund_reason = models.TextField(blank=True, help_text="Reason for refund eligibility or denial")

    # Overall Lifecycle Status
    STATUS_CHOICES = (
        ('TOUR_COMPLETED', 'Tour Completed — Awaiting Result'),
        ('AURORA_SUCCESSFUL', 'Experience Successful — Closed'),
        ('AURORA_UNSUCCESSFUL', 'Experience Unsuccessful'),
        ('REATTEMPT_ELIGIBLE', 'Re-attempt Eligible'),
        ('REATTEMPT_SCHEDULED', 'Re-attempt Scheduled'),
        ('REATTEMPT_COMPLETED', 'Re-attempt Completed'),
        ('REFUND_REVIEW', 'Refund Eligibility Under Review'),
        ('REFUND_APPROVED', 'Refund Approved'),
        ('REFUND_PROCESSING', 'Refund Processing'),
        ('REFUNDED', 'Refunded'),
        ('DECLINED', 'Customer Declined — Closed'),
        ('CLOSED', 'Closed'),
    )
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='TOUR_COMPLETED')

    # Audit
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='guarantee_outcomes_resolved'
    )
    admin_notes = models.TextField(blank=True, help_text="Internal admin notes about this guarantee case")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Guarantee Outcome"
        verbose_name_plural = "Guarantee Outcomes"

    def __str__(self):
        return f"Guarantee: {self.booking.booking_ref} — {self.get_status_display()}"

    @property
    def can_reattempt(self):
        """Check if more re-attempts are allowed under the policy."""
        return (
            self.aurora_result == 'UNSUCCESSFUL'
            and self.reattempt_count < self.policy.max_reattempts
            and self.policy.guarantee_type in ('REATTEMPT_ONLY', 'REATTEMPT_THEN_REFUND')
        )

    @property
    def can_request_refund(self):
        """Check if refund is eligible under the policy."""
        if not self.policy.refund_eligible:
            return False
        if self.policy.guarantee_type == 'REFUND_ONLY':
            return self.aurora_result == 'UNSUCCESSFUL'
        if self.policy.guarantee_type == 'REATTEMPT_THEN_REFUND':
            return (
                self.aurora_result == 'UNSUCCESSFUL'
                and self.reattempt_count >= self.policy.max_reattempts
            )
        return False


class GuaranteeAuditLog(models.Model):
    """
    Immutable audit trail for every action in the guarantee lifecycle.
    Records dates, status changes, reasons, staff/admin actions, and
    references to original and re-attempt bookings.
    """
    outcome = models.ForeignKey(
        GuaranteeOutcome, on_delete=models.CASCADE, related_name='audit_logs'
    )

    ACTION_CHOICES = (
        ('OUTCOME_CREATED', 'Guarantee Outcome Created'),
        ('RESULT_RECORDED', 'Aurora/Experience Result Recorded'),
        ('REATTEMPT_ELIGIBLE', 'Marked Re-attempt Eligible'),
        ('REATTEMPT_SCHEDULED', 'Re-attempt Scheduled'),
        ('REATTEMPT_COMPLETED', 'Re-attempt Completed'),
        ('REFUND_REVIEW_STARTED', 'Refund Eligibility Review Started'),
        ('REFUND_APPROVED', 'Refund Approved'),
        ('REFUND_DENIED', 'Refund Denied'),
        ('REFUND_PROCESSING', 'Refund Processing Initiated'),
        ('REFUND_COMPLETED', 'Refund Completed'),
        ('CUSTOMER_DECLINED', 'Customer Declined Re-attempt/Refund'),
        ('STATUS_CHANGED', 'Status Changed'),
        ('NOTE_ADDED', 'Admin Note Added'),
        ('CLOSED', 'Outcome Closed'),
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)

    old_status = models.CharField(max_length=25, blank=True)
    new_status = models.CharField(max_length=25, blank=True)

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='guarantee_audit_actions'
    )
    reason = models.TextField(blank=True, help_text="Reason for this action")

    # Cross-references as requested by client
    metadata = models.JSONField(
        default=dict, blank=True,
        help_text="Additional structured data: booking refs, departure IDs, refund amounts, etc."
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Guarantee Audit Log"
        verbose_name_plural = "Guarantee Audit Logs"

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.get_action_display()} — {self.outcome.booking.booking_ref}"


