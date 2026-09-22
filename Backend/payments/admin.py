from django.contrib import admin
from .models import Coupon, PaymentIntent, Refund, Receipt, CouponUsage
from .services import RefundService

class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    readonly_fields = ('booking', 'user', 'discount_applied', 'applied_at')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'applicable_to', 'is_active', 'used_count')
    list_filter = ('is_active', 'applicable_to', 'discount_type')
    search_fields = ('code',)
    inlines = [CouponUsageInline]

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'booking', 'user', 'discount_applied', 'applied_at')
    list_filter = ('applied_at',)
    search_fields = ('coupon__code', 'booking__booking_ref', 'user__email')
    readonly_fields = ('applied_at',)


class RefundInline(admin.TabularInline):
    model = Refund
    extra = 0
    readonly_fields = ('stripe_refund_id', 'amount', 'reason', 'status', 'initiated_by', 'approved_by')

@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = ('stripe_payment_intent_id', 'booking', 'amount', 'currency', 'status')
    list_filter = ('status',)
    search_fields = ('stripe_payment_intent_id', 'booking__booking_ref')
    inlines = [RefundInline]
    actions = ['issue_full_refund']

    @admin.action(description="💸 Issue full refund via Stripe")
    def issue_full_refund(self, request, queryset):
        results = []
        for pi in queryset.filter(status='succeeded'):
            result = RefundService.create_stripe_refund(pi, pi.amount)
            if result['success']:
                results.append(f"{pi.booking.booking_ref}: €{pi.amount} refunded (Stripe: {result['stripe_refund_id']})")
            else:
                results.append(f"{pi.booking.booking_ref}: FAILED - {result['error']}")
        self.message_user(request, ' | '.join(results) if results else "No eligible payments selected.")

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('stripe_refund_id', 'payment_intent', 'amount', 'status')
    list_filter = ('status',)
    search_fields = ('stripe_refund_id',)

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_number', 'booking', 'generated_at', 'sent_at')
    search_fields = ('receipt_number', 'booking__booking_ref')

