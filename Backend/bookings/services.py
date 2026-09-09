import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from django.db import transaction
from django.utils import timezone
from .models import Booking, TourBooking, TourBookingGuest, ChauffeurBooking, BookingStatusLog
from tours.models import Tour, TourDate, Departure, DepartureCapacity, VehicleType
from tours.services import TourPricingService, DepartureService
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
        tour_date: Optional[TourDate] = None,
        departure: Optional[Departure] = None,
        vehicle_type: Optional[VehicleType] = None,
        adults: int = 1,
        children: int = 0,
        guests_info: Optional[List[Dict[str, Any]]] = None,
        coupon_code: Optional[str] = None,
        customer_notes: Optional[str] = None,
        dietary_requirements: Optional[str] = None,
        special_requests: Optional[str] = None,
        source: str = 'DIRECT',
        external_reference: Optional[str] = None,
        is_held: bool = False,
        hold_minutes: int = 15,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Atomically creates a complete Tour reservation with Departure & Capacity support:
        1. Validates departure & vehicle type capacity (or legacy tour_date)
        2. Calculates departure/vehicle-tier pricing
        3. Applies promotional coupon if valid
        4. Atomically locks capacity (row-level select_for_update)
        5. Saves Booking, TourBooking, and TourBookingGuest entries
        6. Logs initial state into BookingStatusLog
        """
        total_guests = adults + children
        if total_guests < 1:
            return {"success": False, "error": "Total guests must be at least 1."}

        # Determine if this is a Departure-based booking or legacy TourDate booking
        if departure is not None:
            # Resolve vehicle type
            if vehicle_type is None:
                vehicle_type = VehicleType.objects.filter(is_active=True).first()
                if not vehicle_type:
                    return {"success": False, "error": "No active vehicle types available in system."}

            # 1. Availability validation via DepartureService
            avail = DepartureService.check_availability(departure, vehicle_type, total_guests)
            if not avail["available"]:
                return {"success": False, "error": avail["error"]}

            dc = avail["capacity"]

            # 2. Price calculation via DepartureService
            pricing = DepartureService.calculate_price(
                tour=tour,
                vehicle_type=vehicle_type,
                departure_capacity=dc,
                adults=adults,
                children=children
            )
            subtotal = pricing["final_total"]
            currency = pricing["currency"]

            # 3. Apply Coupon if supplied
            discount_amount = Decimal('0.00')
            applied_coupon = None
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

            # 4. Atomic capacity lock on DepartureCapacity
            capacity_locked = DepartureService.reserve_capacity(dc.id, total_guests)
            if not capacity_locked:
                return {"success": False, "error": "Spots just filled up. Please select another vehicle or departure."}

            # Link legacy tour_date if matching date exists
            if not tour_date:
                tour_date = TourDate.objects.filter(tour=tour, start_date=departure.date).first()

            departure_capacity = dc

        elif tour_date is not None:
            # Legacy TourDate flow
            avail = TourPricingService.check_availability(tour, tour_date, total_guests)
            if not avail["available"]:
                return {"success": False, "error": avail["error"]}

            pricing = TourPricingService.calculate_price(
                tour=tour,
                tour_date=tour_date,
                adults=adults,
                children=children
            )
            subtotal = pricing["final_total"]
            currency = pricing["currency"]

            discount_amount = Decimal('0.00')
            applied_coupon = None
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

            capacity_locked = TourPricingService.reserve_capacity(tour_date, total_guests)
            if not capacity_locked:
                return {"success": False, "error": "Spots just filled up. Please select another date."}

            # Look for matching departure
            departure = Departure.objects.filter(tour=tour, date=tour_date.start_date).first()
            departure_capacity = None
            if departure:
                default_vt = VehicleType.objects.filter(slug='micro').first() or VehicleType.objects.first()
                if default_vt:
                    departure_capacity = DepartureCapacity.objects.filter(departure=departure, vehicle_type=default_vt).first()
                    vehicle_type = default_vt
        else:
            return {"success": False, "error": "A departure or tour date must be selected."}

        # 5. Determine initial status and hold expiry
        hold_expires_at = None
        if status:
            initial_status = status
        elif is_held:
            initial_status = 'HELD'
            hold_expires_at = timezone.now() + timedelta(minutes=hold_minutes)
        elif source in ['MANUAL', 'GETYOURGUIDE', 'VIATOR']:
            initial_status = 'CONFIRMED'
        else:
            initial_status = 'PENDING'

        # 6. Create Booking Header
        booking_ref = cls.generate_booking_ref()
        booking = Booking.objects.create(
            booking_ref=booking_ref,
            booking_type='TOUR',
            customer=customer,
            coupon=applied_coupon,
            status=initial_status,
            source=source,
            external_reference=external_reference,
            hold_expires_at=hold_expires_at,
            subtotal=subtotal,
            discount_amount=discount_amount,
            total_amount=final_total,
            currency=currency,
            customer_notes=customer_notes
        )

        # 7. Create Tour Booking Details
        tour_booking = TourBooking.objects.create(
            booking=booking,
            tour=tour,
            tour_date=tour_date,
            departure=departure,
            departure_capacity=departure_capacity,
            vehicle_type=vehicle_type,
            adults=adults,
            children=children,
            total_guests=total_guests,
            special_requests=special_requests,
            dietary_requirements=dietary_requirements
        )

        # 8. Record individual guests
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

        # 9. Record coupon audit log if coupon was used
        if applied_coupon:
            CouponService.record_usage(
                coupon=applied_coupon,
                booking=booking,
                user=customer,
                discount_applied=discount_amount
            )

        # 10. Initial Status Log
        BookingStatusLog.objects.create(
            booking=booking,
            old_status='NONE',
            new_status=initial_status,
            changed_by=customer,
            reason=f'Tour booking created ({source}) - {initial_status}'
        )

        return {
            "success": True,
            "booking": booking,
            "booking_id": booking.id,
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
        Valid transitions: HELD -> PENDING -> CONFIRMED -> COMPLETED / CANCELLED / EXPIRED / REFUNDED
        """
        old_status = booking.status
        if old_status == new_status:
            return True

        booking.status = new_status
        booking.save(update_fields=['status', 'updated_at'])

        # If booking is cancelled / expired / refunded, restore capacity
        if new_status in ['CANCELLED', 'EXPIRED', 'REFUNDED'] and booking.booking_type == 'TOUR':
            if hasattr(booking, 'tour_booking'):
                tb = booking.tour_booking
                # 1. Release capacity from DepartureCapacity
                if tb.departure_capacity:
                    DepartureService.release_capacity(tb.departure_capacity.id, tb.total_guests)
                # 2. Release capacity from legacy TourDate
                if tb.tour_date:
                    tour_date = tb.tour_date
                    tour_date.booked_count = max(0, tour_date.booked_count - tb.total_guests)
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

    @classmethod
    def create_held_booking(cls, **kwargs) -> Dict[str, Any]:
        """
        Creates a temporary held reservation (defaults to 15 min hold).
        Capacity is deducted immediately, but will auto-expire if payment is not completed.
        """
        kwargs['is_held'] = True
        if 'hold_minutes' not in kwargs:
            kwargs['hold_minutes'] = 15
        return cls.create_tour_booking(**kwargs)

    @classmethod
    @transaction.atomic
    def expire_held_bookings(cls) -> int:
        """
        Management / Cron task to expire unpaid held bookings past hold_expires_at.
        Returns count of expired bookings.
        """
        expired_qs = Booking.objects.filter(
            status='HELD',
            hold_expires_at__lte=timezone.now()
        )
        count = 0
        for b in expired_qs:
            cls.transition_status(
                booking=b,
                new_status='EXPIRED',
                reason='Held booking auto-expired after reservation timeout'
            )
            count += 1
        return count

    @classmethod
    @transaction.atomic
    def rebook_departure(
        cls,
        booking: Booking,
        new_departure: Departure,
        new_vehicle_type: Optional[VehicleType] = None,
        changed_by=None,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        Rebooks a confirmed/pending tour booking to a new departure / vehicle type:
        1. Checks capacity on new departure
        2. Reserves capacity on new DepartureCapacity
        3. Releases capacity on old DepartureCapacity (and old TourDate if applicable)
        4. Updates TourBooking pointers
        5. Logs status change in BookingStatusLog
        """
        if booking.booking_type != 'TOUR' or not hasattr(booking, 'tour_booking'):
            return {"success": False, "error": "Only tour bookings can be rebooked to a new departure."}

        tb = booking.tour_booking
        vt = new_vehicle_type or tb.vehicle_type or VehicleType.objects.filter(slug='micro').first() or VehicleType.objects.first()

        avail = DepartureService.check_availability(new_departure, vt, tb.total_guests)
        if not avail["available"]:
            return {"success": False, "error": f"Cannot rebook: {avail['error']}"}

        new_dc = avail["capacity"]

        # Reserve new capacity first (row lock)
        if not DepartureService.reserve_capacity(new_dc.id, tb.total_guests):
            return {"success": False, "error": "Failed to reserve seats on new departure."}

        # Release old capacity
        if tb.departure_capacity:
            DepartureService.release_capacity(tb.departure_capacity.id, tb.total_guests)
        elif tb.tour_date:
            td = tb.tour_date
            td.booked_count = max(0, td.booked_count - tb.total_guests)
            if td.status == 'SOLD_OUT' and td.booked_count < td.total_capacity:
                td.status = 'AVAILABLE'
            td.save(update_fields=['booked_count', 'status'])

        # Update TourBooking
        old_dep_str = str(tb.departure) if tb.departure else (str(tb.tour_date) if tb.tour_date else "N/A")
        tb.departure = new_departure
        tb.departure_capacity = new_dc
        tb.vehicle_type = vt
        # Also update tour_date if matching date exists
        matching_td = TourDate.objects.filter(tour=tb.tour, start_date=new_departure.date).first()
        tb.tour_date = matching_td
        tb.save(update_fields=['departure', 'departure_capacity', 'vehicle_type', 'tour_date'])

        # Log change
        BookingStatusLog.objects.create(
            booking=booking,
            old_status=booking.status,
            new_status=booking.status,
            changed_by=changed_by,
            reason=reason or f"Rebooked departure from {old_dep_str} to {new_departure} ({vt.name})"
        )

        return {"success": True, "booking": booking, "new_departure": new_departure, "vehicle_type": vt}

