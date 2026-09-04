import uuid
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, Optional, List
from django.db import transaction
from django.utils import timezone
from .models import Booking, TourBooking, TourBookingGuest, ChauffeurBooking, BookingStatusLog
from tours.models import Tour, TourDate
from tours.services import TourPricingService
from chauffeur.models import Vehicle
from chauffeur.services import ChauffeurPricingService
from payments.services import CouponService

class BookingService:
    """
    Manages the lifecycle and state transitions for bookings.
    Adapted from the state machine pattern in the reference project.
    """

    @staticmethod
    def generate_booking_ref() -> str:
        """Generates a human-friendly unique booking reference e.g. NV-2026-A1B2C3"""
        year = datetime.now().year
        token = uuid.uuid4().hex[:6].upper()
        return f"NV-{year}-{token}"

    @classmethod
    @transaction.atomic
    def create_tour_booking(
        cls,
        customer,
        tour: Tour,
        tour_date: TourDate,
        adults: int = 1,
        children: int = 0,
        guests_info: Optional[List[Dict[str, Any]]] = None,
        coupon_code: Optional[str] = None,
        customer_notes: Optional[str] = None,
        dietary_requirements: Optional[str] = None,
        special_requests: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Atomically creates a complete Tour reservation:
        1. Checks date availability & reserves capacity
        2. Calculates pricing breakdown
        3. Applies promotional coupon if valid
        4. Saves Booking, TourBooking, and TourBookingGuest entries
        5. Logs initial state into BookingStatusLog
        """
        total_guests = adults + children

        # 1. Availability validation
        avail = TourPricingService.check_availability(tour, tour_date, total_guests)
        if not avail["available"]:
            return {"success": False, "error": avail["error"]}

        # 2. Price calculation
        pricing = TourPricingService.calculate_price(
            tour=tour,
            tour_date=tour_date,
            adults=adults,
            children=children
        )
        subtotal = pricing["final_total"]
        discount_amount = Decimal('0.00')
        applied_coupon = None

        # 3. Apply Coupon if supplied
        if coupon_code:
            coupon_res = CouponService.validate_coupon(
                coupon_code=coupon_code,
                order_amount=subtotal,
                user=customer,
                service_type='TOUR'
            )
            if coupon_res["valid"]:
                applied_coupon = coupon_res["coupon"]
                discount_amount = coupon_res["discount_amount"]

        final_total = max(Decimal('0.00'), subtotal - discount_amount)

        # 4. Atomic capacity lock
        capacity_locked = TourPricingService.reserve_capacity(tour_date, total_guests)
        if not capacity_locked:
            return {"success": False, "error": "Spots just filled up. Please select another date."}

        # 5. Create Booking Header
        booking_ref = cls.generate_booking_ref()
        booking = Booking.objects.create(
            booking_ref=booking_ref,
            booking_type='TOUR',
            customer=customer,
            coupon=applied_coupon,
            status='PENDING',
            subtotal=subtotal,
            discount_amount=discount_amount,
            total_amount=final_total,
            currency=pricing["currency"],
            customer_notes=customer_notes
        )

        # 6. Create Tour Booking Details
        tour_booking = TourBooking.objects.create(
            booking=booking,
            tour=tour,
            tour_date=tour_date,
            adults=adults,
            children=children,
            total_guests=total_guests,
            special_requests=special_requests,
            dietary_requirements=dietary_requirements
        )

        # 7. Record individual guests
        if guests_info:
            for g in guests_info:
                TourBookingGuest.objects.create(
                    tour_booking=tour_booking,
                    full_name=g.get('full_name', 'Guest'),
                    guest_type=g.get('guest_type', 'ADULT'),
                    date_of_birth=g.get('date_of_birth'),
                    passport_number=g.get('passport_number'),
                    special_needs=g.get('special_needs')
                )

        # 8. Record coupon audit log if coupon was used
        if applied_coupon:
            CouponService.record_usage(
                coupon=applied_coupon,
                booking=booking,
                user=customer,
                discount_applied=discount_amount
            )

        # 9. Initial Status Log
        BookingStatusLog.objects.create(
            booking=booking,
            old_status='NONE',
            new_status='PENDING',
            changed_by=customer,
            reason='Booking created by customer'
        )

        return {
            "success": True,
            "booking": booking,
            "tour_booking": tour_booking,
            "booking_ref": booking_ref,
            "total_amount": final_total
        }

    @classmethod
    @transaction.atomic
    def create_chauffeur_booking(
        cls,
        customer,
        vehicle: Vehicle,
        pickup_address: str,
        destination_address: str,
        pickup_datetime: datetime,
        route_type: str = 'DISTANCE',
        passenger_count: int = 1,
        luggage_count: int = 1,
        distance_km: Decimal = Decimal('25.0'),
        estimated_duration_min: int = 30,
        is_return: bool = False,
        return_pickup_address: Optional[str] = None,
        return_datetime: Optional[datetime] = None,
        special_requests: Optional[str] = None,
        customer_notes: Optional[str] = None,
        coupon_code: Optional[str] = None,
        quote_fare: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Atomically creates a complete VIP Chauffeur reservation:
        1. Calculates fare based on vehicle class, route, and time
        2. Applies promotional coupon if valid
        3. Creates Booking and ChauffeurBooking records
        4. Logs initial state into BookingStatusLog
        """
        # 1. Price calculation
        if quote_fare and quote_fare > 0:
            subtotal = Decimal(str(quote_fare))
            currency = 'EUR'
        else:
            fare_calc = ChauffeurPricingService.calculate_point_to_point(
                vehicle_class=vehicle.vehicle_class,
                distance_km=distance_km,
                duration_min=estimated_duration_min,
                travel_dt=pickup_datetime
            )
            subtotal = fare_calc['final_fare']
            if is_return:
                subtotal = (subtotal * Decimal('1.85')).quantize(Decimal('0.01'))
            currency = fare_calc.get('currency', 'EUR')

        discount_amount = Decimal('0.00')
        applied_coupon = None

        # 2. Apply coupon if supplied
        if coupon_code:
            coupon_res = CouponService.validate_coupon(
                coupon_code=coupon_code,
                order_amount=subtotal,
                user=customer,
                service_type='CHAUFFEUR'
            )
            if coupon_res["valid"]:
                applied_coupon = coupon_res["coupon"]
                discount_amount = coupon_res["discount_amount"]

        final_total = max(Decimal('0.00'), subtotal - discount_amount)

        # 3. Create Booking Header
        booking_ref = cls.generate_booking_ref()
        booking = Booking.objects.create(
            booking_ref=booking_ref,
            booking_type='CHAUFFEUR',
            customer=customer,
            coupon=applied_coupon,
            status='PENDING',
            subtotal=subtotal,
            discount_amount=discount_amount,
            total_amount=final_total,
            currency=currency,
            customer_notes=customer_notes
        )

        # 4. Create Chauffeur Booking Details
        chauffeur_booking = ChauffeurBooking.objects.create(
            booking=booking,
            vehicle=vehicle,
            pickup_address=pickup_address,
            pickup_lat=Decimal('60.169900'),
            pickup_lng=Decimal('24.938400'),
            destination_address=destination_address,
            destination_lat=Decimal('60.192059'),
            destination_lng=Decimal('24.945831'),
            pickup_datetime=pickup_datetime,
            distance_km=distance_km,
            estimated_duration_min=estimated_duration_min,
            quote_id=f"Q-{uuid.uuid4().hex[:8].upper()}",
            route_type=route_type,
            passenger_count=passenger_count,
            luggage_count=luggage_count,
            special_requests=special_requests,
            is_return=is_return,
            return_pickup_address=return_pickup_address or (pickup_address if is_return else None),
            return_datetime=return_datetime
        )

        # 5. Record coupon usage
        if applied_coupon:
            CouponService.record_usage(
                coupon=applied_coupon,
                booking=booking,
                user=customer,
                discount_applied=discount_amount
            )

        # 6. Initial Status Log
        BookingStatusLog.objects.create(
            booking=booking,
            old_status='NONE',
            new_status='PENDING',
            changed_by=customer,
            reason='Chauffeur booking requested by customer'
        )

        return {
            "success": True,
            "booking": booking,
            "chauffeur_booking": chauffeur_booking,
            "booking_ref": booking_ref,
            "total_amount": final_total
        }

    @classmethod
    @transaction.atomic
    def transition_status(cls, booking: Booking, new_status: str, changed_by=None, reason: str = "") -> bool:
        """
        Transitions booking to a new state and records an audit trail.
        Valid transitions: PENDING -> CONFIRMED -> COMPLETED / CANCELLED / REFUNDED
        """
        old_status = booking.status
        if old_status == new_status:
            return True

        booking.status = new_status
        booking.save(update_fields=['status', 'updated_at'])

        # If booking is cancelled, restore capacity
        if new_status in ['CANCELLED', 'REFUNDED'] and booking.booking_type == 'TOUR':
            if hasattr(booking, 'tour_booking') and booking.tour_booking.tour_date:
                tour_date = booking.tour_booking.tour_date
                tour_date.booked_count = max(0, tour_date.booked_count - booking.tour_booking.total_guests)
                if tour_date.status == 'SOLD_OUT' and tour_date.booked_count < tour_date.total_capacity:
                    tour_date.status = 'AVAILABLE'
                tour_date.save(update_fields=['booked_count', 'status'])

        # Record audit log
        BookingStatusLog.objects.create(
            booking=booking,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            reason=reason or f"Status changed from {old_status} to {new_status}"
        )

        return True
