from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Booking, ChauffeurBooking, TourBooking, TourBookingGuest, BookingStatusLog, GuaranteedReattempt
from .services import BookingService
from tours.models import Departure, DepartureCapacity

class ChauffeurBookingInline(admin.StackedInline):
    model = ChauffeurBooking
    extra = 0

class TourBookingInline(admin.StackedInline):
    model = TourBooking
    extra = 0
    fields = ('tour', 'departure', 'vehicle_type', 'departure_capacity', 'tour_date', 'adults', 'children', 'total_guests', 'special_requests', 'dietary_requirements')

class BookingStatusLogInline(admin.TabularInline):
    model = BookingStatusLog
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'changed_by', 'timestamp')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_ref', 'booking_type', 'source_badge', 'customer', 'status', 'payment_method', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'source', 'payment_method', 'payment_status', 'booking_type', 'created_at')
    list_editable = ('status', 'payment_status')
    search_fields = ('booking_ref', 'external_reference', 'customer__email', 'customer__first_name', 'customer__last_name')
    inlines = [ChauffeurBookingInline, TourBookingInline, BookingStatusLogInline]
    actions = ['mark_as_paid', 'mark_as_unpaid', 'cancel_and_restore_capacity', 'mark_failed_experience']

    def source_badge(self, obj):
        colors = {
            'DIRECT': '#3B82F6',
            'GETYOURGUIDE': '#EF4444',
            'VIATOR': '#10B981',
            'MANUAL': '#8B5CF6',
            'HOTEL_AGENT': '#F59E0B',
            'OTHER_OTA': '#6B7280',
        }
        color = colors.get(obj.source, '#6B7280')
        ref_text = f" ({obj.external_reference})" if obj.external_reference else ""
        return mark_safe(
            f'<span style="background:{color}15; color:{color}; border:1px solid {color}40; '
            f'padding:2px 8px; border-radius:4px; font-weight:600; font-size:0.75rem;">'
            f'{obj.get_source_display()}{ref_text}</span>'
        )
    source_badge.short_description = "Channel / Source"

    @admin.action(description="✓ Mark selected bookings as Paid & Confirmed")
    def mark_as_paid(self, request, queryset):
        for b in queryset:
            b.payment_status = 'PAID'
            b.status = 'CONFIRMED'
            b.save(update_fields=['payment_status', 'status', 'updated_at'])
            BookingStatusLog.objects.create(
                booking=b,
                old_status=b.status,
                new_status='CONFIRMED',
                changed_by=request.user,
                reason="Admin marked payment as received / reconciled"
            )
        self.message_user(request, f"{queryset.count()} booking(s) marked as Paid & Confirmed.")

    @admin.action(description="✗ Mark selected bookings as Unpaid")
    def mark_as_unpaid(self, request, queryset):
        queryset.update(payment_status='UNPAID')
        self.message_user(request, f"{queryset.count()} booking(s) marked as Unpaid.")

    @admin.action(description="🚫 Cancel booking & release capacity back to inventory")
    def cancel_and_restore_capacity(self, request, queryset):
        cancelled_count = 0
        for b in queryset:
            if b.status != 'CANCELLED':
                BookingService.transition_status(b, 'CANCELLED', changed_by=request.user, reason="Admin cancelled booking and released seats")
                cancelled_count += 1
        self.message_user(request, f"{cancelled_count} booking(s) cancelled and capacity released back to departure inventory.")

    @admin.action(description="🌌 Mark as Failed Experience (Create Guaranteed Re-attempt)")
    def mark_failed_experience(self, request, queryset):
        created_count = 0
        for b in queryset:
            if b.booking_type == 'TOUR' and hasattr(b, 'tour_booking'):
                tb = b.tour_booking
                dep = tb.departure
                if dep:
                    reattempt, created = GuaranteedReattempt.objects.get_or_create(
                        original_booking=b,
                        original_departure=dep,
                        defaults={
                            'guests_count': tb.total_guests,
                            'reason': 'WEATHER',
                            'status': 'ELIGIBLE'
                        }
                    )
                    if created:
                        created_count += 1
        self.message_user(request, f"Created {created_count} Guaranteed Re-attempt record(s).")


@admin.register(GuaranteedReattempt)
class GuaranteedReattemptAdmin(admin.ModelAdmin):
    list_display = ('original_booking', 'reason', 'status_badge', 'original_departure', 'reattempt_departure', 'guests_count', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('original_booking__booking_ref',)
    actions = ['reserve_next_departure_seats', 'mark_declined']

    def status_badge(self, obj):
        colors = {
            'ELIGIBLE': '#3B82F6',
            'REBOOKED': '#10B981',
            'DECLINED': '#6B7280',
            'EXPIRED': '#EF4444',
        }
        color = colors.get(obj.status, '#6B7280')
        return mark_safe(
            f'<span style="background:{color}15; color:{color}; border:1px solid {color}40; '
            f'padding:2px 8px; border-radius:4px; font-weight:600; font-size:0.75rem;">'
            f'{obj.get_status_display()}</span>'
        )
    status_badge.short_description = "Status"

    @admin.action(description="🔒 Reserve seats on next available departure")
    def reserve_next_departure_seats(self, request, queryset):
        for ra in queryset.filter(status='ELIGIBLE'):
            tour = ra.original_departure.tour
            next_dep = Departure.objects.filter(
                tour=tour,
                date__gt=ra.original_departure.date,
                status='OPEN'
            ).order_by('date', 'time').first()

            if next_dep:
                vt = (
                    ra.original_booking.tour_booking.vehicle_type
                    if hasattr(ra.original_booking, 'tour_booking') and ra.original_booking.tour_booking.vehicle_type
                    else None
                )
                if vt:
                    dc = next_dep.capacities.filter(vehicle_type=vt).first()
                    if dc and dc.public_sellable >= ra.guests_count:
                        DepartureCapacity.objects.filter(id=dc.id).update(
                            reattempt_reserved=models.F('reattempt_reserved') + ra.guests_count
                        )
                        ra.reattempt_departure = next_dep
                        ra.save(update_fields=['reattempt_departure'])
        self.message_user(request, "Seats reserved on next available departure where capacity permitted.")

    @admin.action(description="Declined by customer")
    def mark_declined(self, request, queryset):
        queryset.update(status='DECLINED', resolved_at=timezone.now(), resolved_by=request.user)
        self.message_user(request, "Selected re-attempts marked as declined.")


@admin.register(TourBookingGuest)
class TourBookingGuestAdmin(admin.ModelAdmin):
    list_display = ('tour_booking', 'full_name', 'guest_type')
    search_fields = ('full_name',)

