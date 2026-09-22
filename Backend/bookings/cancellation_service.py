from decimal import Decimal
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from .models import Booking, BookingStatusLog
from tours.models import CancellationPolicy, CancellationRule


class CancellationService:
    """
    Business logic for the tiered cancellation rules engine.
    
    Reads the tour's CancellationPolicy (or site-wide default),
    determines the applicable refund percentage based on hours until departure,
    and processes the cancellation with proper audit trail.
    """

    @staticmethod
    def get_policy_for_booking(booking):
        """Returns the applicable CancellationPolicy for a booking."""
        if booking.booking_type == 'TOUR' and hasattr(booking, 'tour_booking'):
            tour = booking.tour_booking.tour
            if tour.cancellation_policy:
                return tour.cancellation_policy
        # Fallback to site-wide default policy
        return CancellationPolicy.objects.filter(is_default=True, is_active=True).first()

    @staticmethod
    def get_hours_until_departure(booking):
        """Calculates hours remaining until the departure/event datetime."""
        now = timezone.now()

        if booking.booking_type == 'TOUR' and hasattr(booking, 'tour_booking'):
            tb = booking.tour_booking
            if tb.departure:
                dep_dt = timezone.make_aware(
                    datetime.combine(tb.departure.date, tb.departure.time)
                ) if timezone.is_naive(
                    datetime.combine(tb.departure.date, tb.departure.time)
                ) else datetime.combine(tb.departure.date, tb.departure.time)
                return max(0, (dep_dt - now).total_seconds() / 3600)
            elif tb.tour_date:
                dep_dt = timezone.make_aware(
                    datetime.combine(tb.tour_date.start_date, datetime.min.time())
                )
                return max(0, (dep_dt - now).total_seconds() / 3600)

        elif booking.booking_type == 'CHAUFFEUR' and hasattr(booking, 'chauffeur_booking'):
            cb = booking.chauffeur_booking
            if cb.pickup_datetime:
                pickup_dt = cb.pickup_datetime
                if timezone.is_naive(pickup_dt):
                    pickup_dt = timezone.make_aware(pickup_dt)
                return max(0, (pickup_dt - now).total_seconds() / 3600)

        return None

    @classmethod
    def calculate_refund(cls, booking):
        """
        Calculates the refund amount based on the cancellation policy and time until departure.
        
        Returns dict:
            {
                'policy': CancellationPolicy or None,
                'rule': CancellationRule or None,
                'hours_until_departure': float or None,
                'refund_percentage': Decimal,
                'refund_amount': Decimal,
                'original_amount': Decimal,
                'description': str,
            }
        """
        policy = cls.get_policy_for_booking(booking)
        hours = cls.get_hours_until_departure(booking)
        original_amount = booking.total_amount

        if not policy:
            # No policy configured — default to no refund
            return {
                'policy': None,
                'rule': None,
                'hours_until_departure': hours,
                'refund_percentage': Decimal('0.00'),
                'refund_amount': Decimal('0.00'),
                'original_amount': original_amount,
                'description': 'No cancellation policy configured. Contact admin for manual refund.',
            }

        if hours is None:
            # Cannot determine departure time — fall back to most generous rule
            rule = policy.rules.filter(is_active=True).order_by('-hours_before_departure').first()
            pct = rule.refund_percentage if rule else Decimal('0.00')
            desc = rule.description if rule else 'Unable to determine departure time'
            refund = (original_amount * pct / Decimal('100')).quantize(Decimal('0.01'))
            return {
                'policy': policy,
                'rule': rule,
                'hours_until_departure': None,
                'refund_percentage': pct,
                'refund_amount': refund,
                'original_amount': original_amount,
                'description': desc,
            }

        rule = policy.get_applicable_rule(hours)
        if rule:
            pct = rule.refund_percentage
            desc = rule.description or f'{pct}% refund ({hours:.0f}h before departure)'
        else:
            pct = Decimal('0.00')
            desc = 'No applicable rule found — no refund'

        refund = (original_amount * pct / Decimal('100')).quantize(Decimal('0.01'))
        return {
            'policy': policy,
            'rule': rule,
            'hours_until_departure': hours,
            'refund_percentage': pct,
            'refund_amount': refund,
            'original_amount': original_amount,
            'description': desc,
        }

    @classmethod
    @transaction.atomic
    def process_cancellation(cls, booking, user=None, reason=''):
        """
        Full cancellation workflow:
        1. Calculate refund based on policy
        2. Transition booking to CANCELLED (releases capacity via BookingService)
        3. Log the cancellation with refund details in BookingStatusLog
        
        Returns the refund calculation dict.
        """
        from .services import BookingService

        refund_calc = cls.calculate_refund(booking)

        cancel_reason = reason or (
            f"Cancelled by {'admin' if user and user.is_staff else 'customer'}. "
            f"Policy: {refund_calc['policy'].name if refund_calc['policy'] else 'None'}. "
            f"Refund: €{refund_calc['refund_amount']} ({refund_calc['refund_percentage']}%). "
            f"{refund_calc['description']}"
        )

        # Transition status (this handles capacity release internally)
        BookingService.transition_status(
            booking=booking,
            new_status='CANCELLED',
            changed_by=user,
            reason=cancel_reason
        )

        return refund_calc
