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
