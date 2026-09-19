from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from .models import (
    Booking, GuaranteePolicy, GuaranteeOutcome, GuaranteeAuditLog
)
from tours.models import Tour, Departure, DepartureCapacity


class GuaranteeService:
    """
    Business logic layer for the Guarantee System.

    Handles the full post-tour guarantee lifecycle:
        Tour Completed → Aurora Result (Successful / Unsuccessful)
            → Re-attempt Eligible → Re-attempt Scheduled → Re-attempt Completed
            OR → Refund Eligibility Review → Refund Approved → Refund Processing → Refunded
            OR → Closed

    All state transitions create immutable GuaranteeAuditLog entries.
    All policy rules (re-attempt count, refund %, window days) are read from
    the admin-configurable GuaranteePolicy model — nothing is hard-coded.
    """

    @classmethod
    @transaction.atomic
    def create_outcome(cls, booking, departure, user=None):
        """
        Creates a GuaranteeOutcome after a tour is completed.
        Automatically determines the policy from the tour's guarantee_policy FK.

        Returns: (outcome, created) tuple
        """
        tour = booking.tour_booking.tour if hasattr(booking, 'tour_booking') else None
        if not tour:
            return None, False

        policy = tour.guarantee_policy
        if not policy:
            return None, False

        outcome, created = GuaranteeOutcome.objects.get_or_create(
            booking=booking,
            departure=departure,
            defaults={
                'tour': tour,
                'policy': policy,
                'guests_count': booking.tour_booking.total_guests if hasattr(booking, 'tour_booking') else 1,
                'status': 'TOUR_COMPLETED',
            }
        )

        if created:
            cls._log(outcome, 'OUTCOME_CREATED', '', 'TOUR_COMPLETED', user,
                     reason=f"Guarantee outcome created for {booking.booking_ref} under policy '{policy.name}'",
                     metadata={'booking_ref': booking.booking_ref, 'policy': policy.name, 'tour': tour.title})

        return outcome, created

    @classmethod
    @transaction.atomic
    def record_result(cls, outcome, result, reason='', notes='', user=None):
        """
        Records the aurora/experience result: SUCCESSFUL or UNSUCCESSFUL.

        If successful → closes the outcome.
        If unsuccessful → determines next step based on policy (re-attempt or refund).
        """
        if result not in ('SUCCESSFUL', 'UNSUCCESSFUL'):
            raise ValueError(f"Invalid result: {result}. Must be SUCCESSFUL or UNSUCCESSFUL.")

        old_status = outcome.status
        outcome.aurora_result = result
        outcome.result_recorded_at = timezone.now()
        outcome.result_recorded_by = user
        outcome.result_notes = notes

        if result == 'SUCCESSFUL':
            outcome.status = 'AURORA_SUCCESSFUL'
            outcome.resolved_at = timezone.now()
            outcome.resolved_by = user
        else:
            outcome.unsuccessful_reason = reason or 'WEATHER'
            outcome.status = 'AURORA_UNSUCCESSFUL'

        outcome.save()

        cls._log(outcome, 'RESULT_RECORDED', old_status, outcome.status, user,
                 reason=f"Experience result: {result}. {notes}",
                 metadata={'result': result, 'reason': reason})

        # If unsuccessful, auto-determine next step from policy
        if result == 'UNSUCCESSFUL':
            if outcome.can_reattempt:
                cls._mark_reattempt_eligible(outcome, user)
            elif outcome.can_request_refund:
                cls._start_refund_review(outcome, user)

        return outcome

    @classmethod
    @transaction.atomic
    def schedule_reattempt(cls, outcome, reattempt_departure, user=None):
        """
        Schedules a re-attempt on a specific departure.
        Reserves seats on the departure capacity and updates the outcome status.
        """
        if not outcome.can_reattempt:
            raise ValueError("This outcome is not eligible for re-attempt under its policy.")

        old_status = outcome.status
        outcome.reattempt_departure = reattempt_departure
        outcome.reattempt_count += 1
        outcome.status = 'REATTEMPT_SCHEDULED'
        outcome.save()

        # Reserve seats on the departure
        vt = (outcome.booking.tour_booking.vehicle_type
              if hasattr(outcome.booking, 'tour_booking') and outcome.booking.tour_booking.vehicle_type
              else None)
        if vt:
            dc = reattempt_departure.capacities.filter(vehicle_type=vt).first()
            if dc:
                DepartureCapacity.objects.filter(id=dc.id).update(
                    reattempt_reserved=dc.reattempt_reserved + outcome.guests_count
                )

        cls._log(outcome, 'REATTEMPT_SCHEDULED', old_status, 'REATTEMPT_SCHEDULED', user,
                 reason=f"Re-attempt #{outcome.reattempt_count} scheduled for {reattempt_departure}",
                 metadata={
                     'reattempt_count': outcome.reattempt_count,
                     'departure_id': reattempt_departure.id,
                     'departure_date': str(reattempt_departure.date),
                     'max_reattempts': outcome.policy.max_reattempts,
                 })

        return outcome

    @classmethod
    @transaction.atomic
    def complete_reattempt(cls, outcome, result, notes='', user=None):
        """
        Records the result of a re-attempt.
        If unsuccessful and more re-attempts remain → eligible again.
        If unsuccessful and no more re-attempts → move to refund if applicable.
        If successful → close.
        """
        old_status = outcome.status
        outcome.aurora_result = result
        outcome.result_recorded_at = timezone.now()
        outcome.result_recorded_by = user
        outcome.result_notes = notes

        if result == 'SUCCESSFUL':
            outcome.status = 'REATTEMPT_COMPLETED'
            outcome.resolved_at = timezone.now()
            outcome.resolved_by = user
        else:
            outcome.status = 'REATTEMPT_COMPLETED'

        outcome.save()

        cls._log(outcome, 'REATTEMPT_COMPLETED', old_status, outcome.status, user,
                 reason=f"Re-attempt #{outcome.reattempt_count} result: {result}. {notes}",
                 metadata={'result': result, 'reattempt_count': outcome.reattempt_count})

        # Determine next step
        if result == 'UNSUCCESSFUL':
            if outcome.can_reattempt:
                cls._mark_reattempt_eligible(outcome, user)
            elif outcome.can_request_refund:
                cls._start_refund_review(outcome, user)
            else:
                cls._close(outcome, user, reason="All re-attempts exhausted, no refund applicable under policy")
        else:
            cls._close(outcome, user, reason="Re-attempt successful")

        return outcome

    @classmethod
    @transaction.atomic
    def approve_refund(cls, outcome, user=None):
        """Approves refund for the guarantee outcome."""
        if outcome.refund_status not in ('UNDER_REVIEW',):
            raise ValueError("Refund can only be approved when under review.")

        old_status = outcome.status
        outcome.refund_status = 'APPROVED'
        outcome.status = 'REFUND_APPROVED'

        # Calculate refund amount from policy
        refund_pct = outcome.policy.refund_percentage
        original_amount = outcome.booking.total_amount
        outcome.refund_amount = (original_amount * refund_pct / Decimal('100')).quantize(Decimal('0.01'))

        outcome.save()

        cls._log(outcome, 'REFUND_APPROVED', old_status, 'REFUND_APPROVED', user,
                 reason=f"Refund approved: €{outcome.refund_amount} ({refund_pct}% of €{original_amount})",
                 metadata={
                     'refund_amount': str(outcome.refund_amount),
                     'refund_percentage': str(refund_pct),
                     'original_amount': str(original_amount),
                 })

        return outcome

    @classmethod
    @transaction.atomic
    def deny_refund(cls, outcome, reason='', user=None):
        """Denies refund for the guarantee outcome."""
        old_status = outcome.status
        outcome.refund_status = 'DENIED'
        outcome.refund_reason = reason
        outcome.status = 'CLOSED'
        outcome.resolved_at = timezone.now()
        outcome.resolved_by = user
        outcome.save()

        cls._log(outcome, 'REFUND_DENIED', old_status, 'CLOSED', user,
                 reason=f"Refund denied: {reason}")

        return outcome

    @classmethod
    @transaction.atomic
    def process_refund(cls, outcome, refund_record=None, user=None):
        """Marks refund as processing (actual payment refund initiated)."""
        old_status = outcome.status
        outcome.refund_status = 'PROCESSING'
        outcome.status = 'REFUND_PROCESSING'
        if refund_record:
            outcome.refund = refund_record
        outcome.save()

        cls._log(outcome, 'REFUND_PROCESSING', old_status, 'REFUND_PROCESSING', user,
                 reason="Refund processing initiated",
                 metadata={'refund_id': refund_record.id if refund_record else None})

        return outcome

    @classmethod
    @transaction.atomic
    def complete_refund(cls, outcome, user=None):
        """Marks the refund as completed and closes the outcome."""
        old_status = outcome.status
        outcome.refund_status = 'REFUNDED'
        outcome.status = 'REFUNDED'
        outcome.resolved_at = timezone.now()
        outcome.resolved_by = user
        outcome.save()

        cls._log(outcome, 'REFUND_COMPLETED', old_status, 'REFUNDED', user,
                 reason=f"Refund of €{outcome.refund_amount} completed",
                 metadata={'refund_amount': str(outcome.refund_amount)})

        return outcome

    @classmethod
    @transaction.atomic
    def customer_declined(cls, outcome, user=None):
        """Customer declined re-attempt or refund."""
        old_status = outcome.status
        outcome.status = 'DECLINED'
        outcome.resolved_at = timezone.now()
        outcome.resolved_by = user
        outcome.save()

        cls._log(outcome, 'CUSTOMER_DECLINED', old_status, 'DECLINED', user,
                 reason="Customer declined re-attempt/refund offer")

        return outcome

    # --- Internal Helpers ---

    @classmethod
    def _mark_reattempt_eligible(cls, outcome, user=None):
        old_status = outcome.status
        outcome.status = 'REATTEMPT_ELIGIBLE'
        outcome.save(update_fields=['status', 'updated_at'])

        cls._log(outcome, 'REATTEMPT_ELIGIBLE', old_status, 'REATTEMPT_ELIGIBLE', user,
                 reason=f"Eligible for re-attempt ({outcome.reattempt_count}/{outcome.policy.max_reattempts} used)",
                 metadata={'remaining': outcome.policy.max_reattempts - outcome.reattempt_count})

    @classmethod
    def _start_refund_review(cls, outcome, user=None):
        old_status = outcome.status
        outcome.refund_eligible = True
        outcome.refund_status = 'UNDER_REVIEW'
        outcome.status = 'REFUND_REVIEW'
        outcome.save(update_fields=['refund_eligible', 'refund_status', 'status', 'updated_at'])

        cls._log(outcome, 'REFUND_REVIEW_STARTED', old_status, 'REFUND_REVIEW', user,
                 reason=f"Refund eligibility review started (policy: {outcome.policy.refund_percentage}% refund)")

    @classmethod
    def _close(cls, outcome, user=None, reason=''):
        old_status = outcome.status
        outcome.status = 'CLOSED'
        outcome.resolved_at = timezone.now()
        outcome.resolved_by = user
        outcome.save()

        cls._log(outcome, 'CLOSED', old_status, 'CLOSED', user, reason=reason)

    @staticmethod
    def _log(outcome, action, old_status, new_status, user=None, reason='', metadata=None):
        """Creates an immutable audit log entry."""
        GuaranteeAuditLog.objects.create(
            outcome=outcome,
            action=action,
            old_status=old_status,
            new_status=new_status,
            performed_by=user,
            reason=reason,
            metadata=metadata or {},
        )
