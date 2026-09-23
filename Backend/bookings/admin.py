from django.contrib import admin
from django.db import models
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import (
    Booking, ChauffeurBooking, TourBooking, TourBookingGuest, BookingStatusLog,
    GuaranteedReattempt, GuaranteePolicy, GuaranteeOutcome, GuaranteeAuditLog,
    GuestInfo, ChildSeatRequest, BookingAnswer, BookingAddon
)
from .services import BookingService
from .cancellation_service import CancellationService
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

class ChildSeatRequestInline(admin.TabularInline):
    model = ChildSeatRequest
    extra = 0
    fields = ('seat_type', 'quantity', 'child_age', 'approx_weight_kg', 'notes')

class BookingAddonInline(admin.TabularInline):
    model = BookingAddon
    extra = 0
    readonly_fields = ('extra_service', 'quantity', 'unit_price', 'total_price')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_ref', 'booking_type', 'source_badge', 'customer', 'status', 'payment_method', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'source', 'payment_method', 'payment_status', 'booking_type', 'created_at')
    list_editable = ('status', 'payment_status')
    search_fields = ('booking_ref', 'external_reference', 'customer__email', 'customer__first_name', 'customer__last_name')
    inlines = [ChauffeurBookingInline, TourBookingInline, BookingStatusLogInline, ChildSeatRequestInline, BookingAddonInline]
    actions = ['mark_as_paid', 'mark_as_unpaid', 'cancel_and_restore_capacity', 'cancel_with_refund_calc', 'mark_failed_experience']

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

    @admin.action(description="📋 Cancel with refund calculation (Cancellation Policy)")
    def cancel_with_refund_calc(self, request, queryset):
        results = []
        for b in queryset:
            if b.status != 'CANCELLED':
                refund_calc = CancellationService.process_cancellation(b, user=request.user)
                results.append(
                    f"{b.booking_ref}: {refund_calc['refund_percentage']}% refund = €{refund_calc['refund_amount']} "
                    f"({refund_calc['description']})"
                )
        if results:
            self.message_user(request, f"Cancelled {len(results)} booking(s). " + ' | '.join(results))
        else:
            self.message_user(request, "No bookings were cancelled (already cancelled or empty).")

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


class BookingAnswerInline(admin.TabularInline):
    model = BookingAnswer
    extra = 0
    readonly_fields = ('question', 'answer_text')


@admin.register(TourBooking)
class TourBookingAdmin(admin.ModelAdmin):
    list_display = ('booking', 'tour', 'departure', 'vehicle_type', 'pickup_location', 'adults', 'children', 'total_guests')
    list_filter = ('tour', 'vehicle_type')
    search_fields = ('booking__booking_ref', 'tour__title')
    raw_id_fields = ('booking', 'departure', 'departure_capacity', 'tour_date')
    inlines = [BookingAnswerInline]


@admin.register(BookingAnswer)
class BookingAnswerAdmin(admin.ModelAdmin):
    list_display = ('tour_booking', 'question', 'answer_text')
    search_fields = ('tour_booking__booking__booking_ref', 'question__question_text', 'answer_text')



@admin.register(GuaranteedReattempt)
class GuaranteedReattemptAdmin(admin.ModelAdmin):
    list_display = ('original_booking', 'reason', 'status_badge', 'original_departure', 'reattempt_departure', 'guests_count', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('original_booking__booking_ref',)
    raw_id_fields = ('original_booking', 'reattempt_booking', 'original_departure', 'reattempt_departure')
    actions = ['reserve_next_departure_seats', 'mark_declined']

    def save_model(self, request, obj, form, change):
        if not change and not obj.resolved_by:
            obj.resolved_by = request.user
        if not obj.original_departure_id and obj.original_booking_id:
            if hasattr(obj.original_booking, 'tour_booking') and obj.original_booking.tour_booking.departure:
                obj.original_departure = obj.original_booking.tour_booking.departure
            elif hasattr(obj.original_booking, 'tour_booking') and obj.original_booking.tour_booking.tour:
                obj.original_departure = obj.original_booking.tour_booking.tour.departures.first()
        if not obj.guests_count:
            if hasattr(obj.original_booking, 'tour_booking') and obj.original_booking.tour_booking.total_guests:
                obj.guests_count = obj.original_booking.tour_booking.total_guests
            else:
                obj.guests_count = 1
        super().save_model(request, obj, form, change)

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
            tour = ra.original_departure.tour if ra.original_departure else (ra.original_booking.tour_booking.tour if hasattr(ra.original_booking, 'tour_booking') else None)
            if not tour:
                continue
            date_filter = ra.original_departure.date if ra.original_departure else timezone.now().date()
            next_dep = Departure.objects.filter(
                tour=tour,
                date__gt=date_filter,
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


@admin.register(GuestInfo)
class GuestInfoAdmin(admin.ModelAdmin):
    list_display = ('tour_booking', 'full_name', 'guest_type', 'date_of_birth')
    search_fields = ('full_name', 'passport_number')


# =============================================================================
# GUARANTEE SYSTEM ADMIN
# =============================================================================

@admin.register(GuaranteePolicy)
class GuaranteePolicyAdmin(admin.ModelAdmin):
    list_display = ('name', 'guarantee_type_badge', 'max_reattempts', 'refund_eligible', 'refund_percentage', 'is_active')
    list_filter = ('guarantee_type', 'refund_eligible', 'is_active')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'guarantee_type', 'is_active')}),
        ('Re-attempt Rules', {
            'fields': ('max_reattempts', 'reattempt_window_days'),
            'description': 'Configure how many re-attempts are allowed and within what timeframe.'
        }),
        ('Refund Rules', {
            'fields': ('refund_eligible', 'refund_percentage', 'refund_review_required'),
            'description': 'Configure refund eligibility and approval workflow.'
        }),
        ('Customer-Facing Information', {
            'fields': ('description', 'terms_and_conditions'),
            'classes': ('collapse',),
        }),
    )

    def guarantee_type_badge(self, obj):
        colors = {
            'REATTEMPT_ONLY': ('#DBEAFE', '#2563EB'),
            'REFUND_ONLY': ('#FEE2E2', '#DC2626'),
            'REATTEMPT_THEN_REFUND': ('#D1FAE5', '#059669'),
        }
        bg, fg = colors.get(obj.guarantee_type, ('#F1F5F9', '#475569'))
        return mark_safe(f'<span style="background:{bg}; color:{fg}; padding:3px 8px; border-radius:4px; font-weight:600; font-size:0.8rem;">{obj.get_guarantee_type_display()}</span>')
    guarantee_type_badge.short_description = "Type"


class GuaranteeAuditLogInline(admin.TabularInline):
    model = GuaranteeAuditLog
    extra = 0
    readonly_fields = ('action', 'old_status', 'new_status', 'performed_by', 'reason', 'metadata', 'timestamp')
    ordering = ['-timestamp']

    def has_add_permission(self, request, obj=None):
        return False  # Audit logs are immutable — only created programmatically

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(GuaranteeOutcome)
class GuaranteeOutcomeAdmin(admin.ModelAdmin):
    list_display = ('booking', 'tour', 'aurora_result_badge', 'status_badge', 'policy', 'reattempt_count', 'refund_status', 'created_at')
    list_filter = ('status', 'aurora_result', 'refund_status', 'policy', 'created_at')
    search_fields = ('booking__booking_ref', 'tour__title')
    inlines = [GuaranteeAuditLogInline]
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Booking & Tour', {'fields': ('booking', 'tour', 'policy', 'departure', 'guests_count')}),
        ('Experience Result', {
            'fields': ('aurora_result', 'unsuccessful_reason', 'result_notes', 'result_recorded_at', 'result_recorded_by')
        }),
        ('Re-attempt Tracking', {
            'fields': ('reattempt_count', 'reattempt_departure', 'reattempt_booking')
        }),
        ('Refund Tracking', {
            'fields': ('refund_eligible', 'refund_status', 'refund_amount', 'refund', 'refund_reason')
        }),
        ('Lifecycle Status', {
            'fields': ('status', 'resolved_by', 'resolved_at', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def aurora_result_badge(self, obj):
        colors = {
            'PENDING': ('#FEF3C7', '#D97706'),
            'SUCCESSFUL': ('#D1FAE5', '#059669'),
            'UNSUCCESSFUL': ('#FEE2E2', '#DC2626'),
        }
        bg, fg = colors.get(obj.aurora_result, ('#F1F5F9', '#475569'))
        return mark_safe(f'<span style="background:{bg}; color:{fg}; padding:3px 8px; border-radius:4px; font-weight:600; font-size:0.8rem;">{obj.get_aurora_result_display()}</span>')
    aurora_result_badge.short_description = "Result"

    def status_badge(self, obj):
        color_map = {
            'TOUR_COMPLETED': '#D97706', 'AURORA_SUCCESSFUL': '#059669',
            'AURORA_UNSUCCESSFUL': '#DC2626', 'REATTEMPT_ELIGIBLE': '#2563EB',
            'REATTEMPT_SCHEDULED': '#7C3AED', 'REATTEMPT_COMPLETED': '#059669',
            'REFUND_REVIEW': '#D97706', 'REFUND_APPROVED': '#2563EB',
            'REFUND_PROCESSING': '#7C3AED', 'REFUNDED': '#059669',
            'DECLINED': '#6B7280', 'CLOSED': '#475569',
        }
        color = color_map.get(obj.status, '#6B7280')
        return mark_safe(
            f'<span style="background:{color}15; color:{color}; border:1px solid {color}40; '
            f'padding:2px 8px; border-radius:4px; font-weight:600; font-size:0.75rem;">'
            f'{obj.get_status_display()}</span>'
        )
    status_badge.short_description = "Status"


@admin.register(GuaranteeAuditLog)
class GuaranteeAuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'outcome', 'action', 'old_status', 'new_status', 'performed_by')
    list_filter = ('action', 'timestamp')
    search_fields = ('outcome__booking__booking_ref', 'reason')
    readonly_fields = ('outcome', 'action', 'old_status', 'new_status', 'performed_by', 'reason', 'metadata', 'timestamp')

    def has_add_permission(self, request):
        return False  # Audit logs are immutable

    def has_delete_permission(self, request, obj=None):
        return False

