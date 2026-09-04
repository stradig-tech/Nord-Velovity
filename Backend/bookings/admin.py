from django.contrib import admin
from .models import Booking, ChauffeurBooking, TourBooking, TourBookingGuest, BookingStatusLog

class ChauffeurBookingInline(admin.StackedInline):
    model = ChauffeurBooking
    extra = 0

class TourBookingInline(admin.StackedInline):
    model = TourBooking
    extra = 0

class BookingStatusLogInline(admin.TabularInline):
    model = BookingStatusLog
    extra = 0
    readonly_fields = ('old_status', 'new_status', 'changed_by', 'timestamp')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_ref', 'booking_type', 'customer', 'status', 'payment_method', 'payment_status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'booking_type', 'created_at')
    list_editable = ('status', 'payment_status')
    search_fields = ('booking_ref', 'customer__email', 'customer__first_name', 'customer__last_name')
    inlines = [ChauffeurBookingInline, TourBookingInline, BookingStatusLogInline]
    actions = ['mark_as_paid', 'mark_as_unpaid']

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
                reason="Admin marked offline payment as received"
            )
        self.message_user(request, f"{queryset.count()} booking(s) marked as Paid & Confirmed.")

    @admin.action(description="✗ Mark selected bookings as Unpaid")
    def mark_as_unpaid(self, request, queryset):
        queryset.update(payment_status='UNPAID')
        self.message_user(request, f"{queryset.count()} booking(s) marked as Unpaid.")

@admin.register(TourBookingGuest)
class TourBookingGuestAdmin(admin.ModelAdmin):
    list_display = ('tour_booking', 'full_name', 'guest_type')
    search_fields = ('full_name',)
