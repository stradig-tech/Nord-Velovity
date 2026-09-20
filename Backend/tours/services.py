from decimal import Decimal
from datetime import date
from typing import Dict, Any, Optional, List
from django.db import transaction
from django.db.models import F
from django.core.exceptions import ValidationError
from .models import Tour, TourDate, TourPricing, Departure, DepartureCapacity, VehicleType, TourOptionPricing

class TourPricingService:
    """
    Pricing and Availability Engine for NordVelocity Tours.
    Adapted from the robust calculation pipeline of the reference Tour project.
    """

    @staticmethod
    def check_availability(tour: Tour, tour_date: TourDate, requested_guests: int) -> Dict[str, Any]:
        """
        Validates if the tour has enough capacity on the requested date.
        """
        if tour_date.tour_id != tour.id:
            return {"available": False, "error": "Selected date does not belong to this tour."}

        if tour_date.status != 'AVAILABLE':
            return {"available": False, "error": f"This date is currently {tour_date.get_status_display()}."}

        remaining_capacity = tour_date.total_capacity - tour_date.booked_count
        if remaining_capacity < requested_guests:
            return {
                "available": False,
                "error": f"Only {remaining_capacity} spot(s) remaining for this date."
            }

        return {"available": True, "remaining_capacity": remaining_capacity}

    @staticmethod
    def calculate_price(
        tour: Tour,
        tour_date: Optional[TourDate] = None,
        adults: int = 1,
        children: int = 0,
        extras: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculates the complete price breakdown for a tour booking:
        - Adult price & Child price (from TourPricing if defined, or base tour price)
        - Early-bird discounts if booked before deadline
        - Add-on extras (per-person or flat fee)
        - Group discounts for larger parties
        """
        total_guests = adults + children
        if total_guests < 1:
            raise ValidationError("Total guests must be at least 1.")

        currency = 'EUR'
        adult_unit_price = Decimal('0.00')
        child_unit_price = Decimal('0.00')

        # 1. Fetch Tiered / Person-type Pricing
        adult_pricing = tour.pricing.filter(label__iexact='Adult').first()
        child_pricing = tour.pricing.filter(label__iexact='Child').first()

        today = date.today()

        # Determine adult unit price (with early-bird check if applicable)
        if adult_pricing:
            currency = adult_pricing.currency
            if adult_pricing.early_bird_price and adult_pricing.early_bird_deadline and today <= adult_pricing.early_bird_deadline:
                adult_unit_price = adult_pricing.early_bird_price
            else:
                adult_unit_price = adult_pricing.price
        else:
            # Fallback to default starting tour pricing if none specifically labelled 'Adult'
            first_pricing = tour.pricing.first()
            if first_pricing:
                currency = first_pricing.currency
                adult_unit_price = first_pricing.price
            else:
                adult_unit_price = Decimal('100.00')

        # Determine child unit price (default to 50% of adult price if not explicitly configured)
        if child_pricing:
            if child_pricing.early_bird_price and child_pricing.early_bird_deadline and today <= child_pricing.early_bird_deadline:
                child_unit_price = child_pricing.early_bird_price
            else:
                child_unit_price = child_pricing.price
        else:
            child_unit_price = (adult_unit_price * Decimal('0.5')).quantize(Decimal('0.01'))

        adults_total = (adult_unit_price * adults).quantize(Decimal('0.01'))
        children_total = (child_unit_price * children).quantize(Decimal('0.01'))
        subtotal = adults_total + children_total

        # 2. Add-on Extras (e.g. thermal suits, private transport)
        extras_total = Decimal('0.00')
        extras_breakdown = []
        if extras:
            for extra in extras:
                # Expecting: {'name': 'Thermal Boots', 'price': 15.00, 'per_person': True}
                price = Decimal(str(extra.get('price', 0)))
                per_person = extra.get('per_person', False)
                item_total = price * total_guests if per_person else price
                extras_total += item_total
                extras_breakdown.append({
                    'name': extra.get('name', 'Extra Item'),
                    'unit_price': price,
                    'per_person': per_person,
                    'total': item_total
                })

        # 3. Group Discounts (e.g., 5% off for 4+ guests, 10% off for 8+ guests)
        group_discount_percent = Decimal('0.00')
        if total_guests >= 8:
            group_discount_percent = Decimal('0.10') # 10%
        elif total_guests >= 4:
            group_discount_percent = Decimal('0.05') # 5%

        discount_amount = (subtotal * group_discount_percent).quantize(Decimal('0.01'))
        final_total = (subtotal - discount_amount + extras_total).quantize(Decimal('0.01'))

        return {
            'currency': currency,
            'adults': adults,
            'adult_unit_price': adult_unit_price,
            'adults_total': adults_total,
            'children': children,
            'child_unit_price': child_unit_price,
            'children_total': children_total,
            'total_guests': total_guests,
            'subtotal': subtotal,
            'group_discount_percent': float(group_discount_percent * 100),
            'discount_amount': discount_amount,
            'extras': extras_breakdown,
            'extras_total': extras_total,
            'final_total': final_total
        }

    @staticmethod
    def reserve_capacity(tour_date: TourDate, guest_count: int) -> bool:
        """
        Atomically increments booked_count to guarantee race-condition-free reservations.
        """
        updated = TourDate.objects.filter(
            id=tour_date.id,
            status='AVAILABLE',
            total_capacity__gte=F('booked_count') + guest_count
        ).update(booked_count=F('booked_count') + guest_count)

        if updated:
            # Refresh from DB and check if it has reached full capacity
            tour_date.refresh_from_db()
            if tour_date.booked_count >= tour_date.total_capacity:
                tour_date.status = 'SOLD_OUT'
                tour_date.save(update_fields=['status'])
            return True
        return False


class DepartureService:
    """
    Central Departure & Multi-Capacity Inventory Service for OTA & Direct Bookings.
    Implements:
    - Independent per-vehicle-type inventory checks (Private Car, Micro, Group Bus)
    - Row-level locking (select_for_update) to prevent overselling
    - Unified channel capacity deduction
    - Guaranteed re-attempt hold reservation and release
    """

    @staticmethod
    def check_availability(
        departure: Departure,
        vehicle_type: VehicleType,
        requested_guests: int
    ) -> Dict[str, Any]:
        """
        Validates if the requested departure and vehicle type has enough public sellable seats.
        """
        if departure.status != 'OPEN':
            return {
                "available": False,
                "error": f"This departure is currently {departure.get_status_display().lower()}."
            }

        try:
            dc = departure.capacities.get(vehicle_type=vehicle_type)
        except DepartureCapacity.DoesNotExist:
            return {
                "available": False,
                "error": f"{vehicle_type.name} is not offered for this departure.",
                "sellable": 0
            }

        sellable = dc.public_sellable
        if sellable < requested_guests:
            return {
                "available": False,
                "error": f"Only {sellable} seat(s) available for {vehicle_type.name}.",
                "sellable": sellable,
                "capacity": dc
            }

        return {
            "available": True,
            "sellable": sellable,
            "capacity": dc
        }

    @staticmethod
    @transaction.atomic
    def reserve_capacity(departure_capacity_id: int, guest_count: int) -> bool:
        """
        Locks the DepartureCapacity row with select_for_update() and atomically reserves seats.
        Returns True if reservation succeeded, False if insufficient sellable seats.
        """
        try:
            dc = DepartureCapacity.objects.select_for_update().get(id=departure_capacity_id)
        except DepartureCapacity.DoesNotExist:
            return False

        if dc.public_sellable >= guest_count:
            DepartureCapacity.objects.filter(id=dc.id).update(booked_count=F('booked_count') + guest_count)
            dc.refresh_from_db()

            # If all vehicle types on this departure are now sold out, mark departure status as SOLD_OUT
            dep = dc.departure
            all_sold = True
            for c in dep.capacities.all():
                if c.public_sellable > 0:
                    all_sold = False
                    break
            if all_sold and dep.status == 'OPEN':
                dep.status = 'SOLD_OUT'
                dep.save(update_fields=['status'])

            return True

        return False

    @staticmethod
    @transaction.atomic
    def release_capacity(departure_capacity_id: int, guest_count: int) -> bool:
        """
        Atomically releases seats back to the DepartureCapacity inventory.
        Also re-opens departure status if it was previously marked SOLD_OUT.
        """
        try:
            dc = DepartureCapacity.objects.select_for_update().get(id=departure_capacity_id)
        except DepartureCapacity.DoesNotExist:
            return False

        new_booked = max(0, dc.booked_count - guest_count)
        DepartureCapacity.objects.filter(id=dc.id).update(booked_count=new_booked)
        dc.refresh_from_db()

        dep = dc.departure
        if dep.status == 'SOLD_OUT' and dc.public_sellable > 0:
            dep.status = 'OPEN'
            dep.save(update_fields=['status'])

        return True

    @staticmethod
    @transaction.atomic
    def reserve_reattempt_seats(departure_capacity_id: int, guest_count: int) -> bool:
        """
        Reserves seats for guaranteed re-attempt guests (excluded from public sellable).
        """
        try:
            dc = DepartureCapacity.objects.select_for_update().get(id=departure_capacity_id)
        except DepartureCapacity.DoesNotExist:
            return False

        if dc.public_sellable >= guest_count:
            DepartureCapacity.objects.filter(id=dc.id).update(reattempt_reserved=F('reattempt_reserved') + guest_count)
            dc.refresh_from_db()
            return True
        return False

    @staticmethod
    @transaction.atomic
    def release_reattempt_seats(departure_capacity_id: int, guest_count: int) -> bool:
        """
        Releases guaranteed re-attempt reserved seats back to public sellable.
        """
        try:
            dc = DepartureCapacity.objects.select_for_update().get(id=departure_capacity_id)
        except DepartureCapacity.DoesNotExist:
            return False

        new_reserved = max(0, dc.reattempt_reserved - guest_count)
        DepartureCapacity.objects.filter(id=dc.id).update(reattempt_reserved=new_reserved)
        dc.refresh_from_db()
        return True

    @staticmethod
    def calculate_price(
        tour: Tour,
        vehicle_type: VehicleType,
        departure_capacity: Optional[DepartureCapacity] = None,
        adults: int = 1,
        children: int = 0,
        extras: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Calculates pricing based on:
        1. DepartureCapacity price overrides (if set)
        2. TourOptionPricing for (tour, vehicle_type)
        3. Fallback to Tour base price
        Includes early bird discounts, add-ons, and group party discounts.
        """
        total_guests = adults + children
        if total_guests < 1:
            raise ValidationError("Total guests must be at least 1.")

        currency = 'EUR'
        adult_unit_price = None
        child_unit_price = None
        today = date.today()

        # 1. Check per-departure capacity price override
        if departure_capacity:
            if departure_capacity.price_override_adult is not None:
                adult_unit_price = departure_capacity.price_override_adult
            if departure_capacity.price_override_child is not None:
                child_unit_price = departure_capacity.price_override_child

        # 2. Check TourOptionPricing
        option_pricing = TourOptionPricing.objects.filter(
            tour=tour,
            vehicle_type=vehicle_type,
            is_active=True
        ).first()

        if adult_unit_price is None:
            if option_pricing:
                currency = option_pricing.currency
                if option_pricing.early_bird_price and option_pricing.early_bird_deadline and today <= option_pricing.early_bird_deadline:
                    adult_unit_price = option_pricing.early_bird_price
                else:
                    adult_unit_price = option_pricing.adult_price
            else:
                adult_unit_price = tour.base_price

        if child_unit_price is None:
            if option_pricing:
                if option_pricing.early_bird_child_price and option_pricing.early_bird_deadline and today <= option_pricing.early_bird_deadline:
                    child_unit_price = option_pricing.early_bird_child_price
                else:
                    child_unit_price = option_pricing.child_price
            else:
                child_unit_price = (adult_unit_price * Decimal('0.5')).quantize(Decimal('0.01'))

        adults_total = (adult_unit_price * adults).quantize(Decimal('0.01'))
        children_total = (child_unit_price * children).quantize(Decimal('0.01'))
        subtotal = adults_total + children_total

        # 3. Add-on extras
        extras_total = Decimal('0.00')
        extras_breakdown = []
        if extras:
            for extra in extras:
                price = Decimal(str(extra.get('price', 0)))
                per_person = extra.get('per_person', False)
                item_total = price * total_guests if per_person else price
                extras_total += item_total
                extras_breakdown.append({
                    'name': extra.get('name', 'Extra Item'),
                    'unit_price': price,
                    'per_person': per_person,
                    'total': item_total
                })

        # 4. Group discount
        group_discount_percent = Decimal('0.00')
        if total_guests >= 8:
            group_discount_percent = Decimal('0.10')
        elif total_guests >= 4:
            group_discount_percent = Decimal('0.05')

        discount_amount = (subtotal * group_discount_percent).quantize(Decimal('0.01'))
        final_total = (subtotal - discount_amount + extras_total).quantize(Decimal('0.01'))

        return {
            'currency': currency,
            'vehicle_type': vehicle_type.name,
            'adults': adults,
            'adult_unit_price': adult_unit_price,
            'adults_total': adults_total,
            'children': children,
            'child_unit_price': child_unit_price,
            'children_total': children_total,
            'total_guests': total_guests,
            'subtotal': subtotal,
            'group_discount_percent': float(group_discount_percent * 100),
            'discount_amount': discount_amount,
            'extras': extras_breakdown,
            'extras_total': extras_total,
            'final_total': final_total
        }

