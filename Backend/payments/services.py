from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional
from django.utils import timezone
from .models import Coupon, CouponUsage

class CouponService:
    """
    Business logic for validating and applying promotion codes.
    Adapted from the Coupon validation pipeline in the reference project.
    """

    @staticmethod
    def validate_coupon(coupon_code: str, order_amount: Decimal, user=None, service_type: str = 'TOUR') -> Dict[str, Any]:
        """
        Validates coupon conditions:
        - Active status & valid date window
        - Applicable service type (CHAUFFEUR, TOUR, BOTH)
        - Minimum order threshold
        - Global usage limit & per-user usage limit
        """
        coupon = Coupon.objects.filter(code__iexact=coupon_code.strip()).first()
        if not coupon:
            return {"valid": False, "error": "Coupon code not found."}

        if not coupon.is_active:
            return {"valid": False, "error": "This coupon code is no longer active."}

        now = timezone.now()
        if now < coupon.valid_from:
            return {"valid": False, "error": "This coupon promotion has not started yet."}
        if now > coupon.valid_until:
            return {"valid": False, "error": "This coupon promotion has expired."}

        if coupon.applicable_to != 'BOTH' and coupon.applicable_to != service_type:
            return {"valid": False, "error": f"This coupon can only be applied to {coupon.get_applicable_to_display()} bookings."}

        if coupon.min_order_amount and order_amount < coupon.min_order_amount:
            return {
                "valid": False,
                "error": f"Order minimum of €{coupon.min_order_amount} required to use this coupon."
            }

        if coupon.max_uses and coupon.used_count >= coupon.max_uses:
            return {"valid": False, "error": "This coupon has reached its maximum redemptions."}

        # Per-user usage check if user is authenticated
        if user and user.is_authenticated:
            user_used_count = CouponUsage.objects.filter(coupon=coupon, user=user).count()
            if user_used_count >= 1: # Default 1 redemption per user
                return {"valid": False, "error": "You have already redeemed this coupon."}

        # Calculate discount amount
        if coupon.discount_type == 'PERCENT':
            discount = (order_amount * (coupon.discount_value / Decimal('100.00'))).quantize(Decimal('0.01'))
            if coupon.max_discount_amount and discount > coupon.max_discount_amount:
                discount = coupon.max_discount_amount
        else: # FIXED
            discount = min(coupon.discount_value, order_amount)

        return {
            "valid": True,
            "coupon": coupon,
            "discount_amount": discount,
            "final_amount": max(Decimal('0.00'), order_amount - discount)
        }

    @staticmethod
    def record_usage(coupon: Coupon, booking, user=None, discount_applied: Decimal = Decimal('0.00')) -> CouponUsage:
        """
        Records the redemption in the audit table and increments coupon usage counter.
        """
        usage = CouponUsage.objects.create(
            coupon=coupon,
            booking=booking,
            user=user if user and user.is_authenticated else None,
            discount_applied=discount_applied
        )
        coupon.used_count += 1
        coupon.save(update_fields=['used_count'])
        return usage


class RefundService:
    """
    Handles refund processing via Stripe and PayPal payment gateways.
    Integrates with the Refund model for audit and tracking.
    """

    @staticmethod
    def create_stripe_refund(payment_intent, amount, reason='requested_by_customer'):
        """
        Issues a refund via Stripe API and records it in the Refund model.
        
        Args:
            payment_intent: PaymentIntent model instance
            amount: Decimal amount to refund
            reason: Stripe reason code (requested_by_customer, duplicate, fraudulent)
        
        Returns: dict with success/error
        """
        import stripe
        from django.conf import settings
        from .models import Refund

        stripe.api_key = settings.STRIPE_SECRET_KEY

        try:
            stripe_refund = stripe.Refund.create(
                payment_intent=payment_intent.stripe_payment_intent_id,
                amount=int(amount * 100),  # Stripe uses cents
                reason=reason,
            )

            refund = Refund.objects.create(
                payment_intent=payment_intent,
                stripe_refund_id=stripe_refund.id,
                amount=amount,
                reason=reason,
                status='COMPLETED' if stripe_refund.status == 'succeeded' else 'PENDING',
            )

            return {
                'success': True,
                'refund': refund,
                'stripe_refund_id': stripe_refund.id,
                'status': stripe_refund.status,
            }

        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e),
            }

    @staticmethod
    def create_paypal_refund(booking, amount, reason='Customer requested refund'):
        """
        Issues a refund via PayPal API.
        Note: Requires the PayPal order/capture ID from the booking.
        
        Returns: dict with success/error
        """
        import requests
        from django.conf import settings
        from .models import Refund

        # Get PayPal access token
        auth_response = requests.post(
            'https://api-m.sandbox.paypal.com/v1/oauth2/token',
            headers={'Accept': 'application/json'},
            data={'grant_type': 'client_credentials'},
            auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_SECRET),
        )

        if auth_response.status_code != 200:
            return {'success': False, 'error': 'Failed to authenticate with PayPal'}

        access_token = auth_response.json().get('access_token')

        # Find PayPal capture ID from booking metadata
        paypal_order_id = booking.admin_notes  # Convention: stored in admin_notes during capture
        if not paypal_order_id:
            return {'success': False, 'error': 'No PayPal order ID found for this booking'}

        # Get capture ID from order details
        order_response = requests.get(
            f'https://api-m.sandbox.paypal.com/v2/checkout/orders/{paypal_order_id}',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
        )

        if order_response.status_code != 200:
            return {'success': False, 'error': 'Failed to retrieve PayPal order details'}

        order_data = order_response.json()
        captures = order_data.get('purchase_units', [{}])[0].get('payments', {}).get('captures', [])
        if not captures:
            return {'success': False, 'error': 'No PayPal capture found for this order'}

        capture_id = captures[0]['id']

        # Issue refund
        refund_response = requests.post(
            f'https://api-m.sandbox.paypal.com/v2/payments/captures/{capture_id}/refund',
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            },
            json={
                'amount': {
                    'value': str(amount),
                    'currency_code': booking.currency or 'EUR',
                },
                'note_to_payer': reason,
            }
        )

        if refund_response.status_code in (200, 201):
            refund_data = refund_response.json()
            return {
                'success': True,
                'paypal_refund_id': refund_data.get('id'),
                'status': refund_data.get('status'),
            }

        return {
            'success': False,
            'error': f'PayPal refund failed: {refund_response.text}',
        }

    @staticmethod
    def issue_refund(booking, amount, reason='Admin-initiated refund', initiated_by=None):
        """
        High-level method to issue a refund for any booking, regardless of payment method.
        Automatically detects Stripe vs PayPal vs Offline and routes accordingly.
        """
        from .models import PaymentIntent

        if booking.payment_method == 'STRIPE':
            pi = PaymentIntent.objects.filter(booking=booking, status='succeeded').first()
            if pi:
                return RefundService.create_stripe_refund(pi, amount, reason)
            return {'success': False, 'error': 'No successful Stripe payment found for this booking'}

        elif booking.payment_method == 'PAYPAL':
            return RefundService.create_paypal_refund(booking, amount, reason)

        elif booking.payment_method in ('CASH', 'BANK_TRANSFER'):
            return {
                'success': True,
                'note': f'Offline refund of €{amount} needs to be processed manually. Reason: {reason}',
            }

        return {'success': False, 'error': f'Unsupported payment method: {booking.payment_method}'}
