from decimal import Decimal
from datetime import datetime, time
from typing import Dict, Any, Optional
from django.utils import timezone
from .models import VehicleClass, PricingRule, FixedRoute, Surcharge

class ChauffeurPricingService:
    """
    Calculation engine for VIP Chauffeur services:
    - Distance-based point-to-point transfers (airport, intercity)
    - Fixed routes (e.g., Helsinki Airport -> City Center)
    - Hourly charter bookings
    - Automatic night and weekend surcharges
    """

    @staticmethod
    def get_applicable_surcharges(travel_dt: Optional[datetime] = None) -> Decimal:
        """
        Determines applicable surcharge multiplier or flat additions based on travel time.
        """
        if not travel_dt:
            travel_dt = timezone.now()

        total_surcharge = Decimal('0.00')
        active_surcharges = Surcharge.objects.filter(is_active=True)

        current_time = travel_dt.time()
        day_of_week = travel_dt.weekday() # 0=Mon, 6=Sun

        for sc in active_surcharges:
            is_applicable = False
            
            # Category: NIGHT
            if sc.surcharge_category == 'NIGHT' and sc.start_time and sc.end_time:
                if sc.start_time > sc.end_time: # Crosses midnight (e.g. 22:00 to 06:00)
                    if current_time >= sc.start_time or current_time <= sc.end_time:
                        is_applicable = True
                else:
                    if sc.start_time <= current_time <= sc.end_time:
                        is_applicable = True

            # Category: WEEKEND
            elif sc.surcharge_category == 'WEEKEND':
                if day_of_week in [5, 6]: # Sat / Sun
                    is_applicable = True

            # Specific date
            elif sc.specific_date and sc.specific_date == travel_dt.date():
                is_applicable = True

            if is_applicable:
                total_surcharge += sc.amount

        return total_surcharge

    @classmethod
    def calculate_point_to_point(
        cls,
        vehicle_class: VehicleClass,
        distance_km: Decimal,
        duration_min: Optional[int] = None,
        travel_dt: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculates distance-based fare using active PricingRule.
        """
        rule = vehicle_class.pricing_rules.filter(is_active=True).first()
        if not rule:
            # Safe defaults if no rule configured yet
            base_fare = Decimal('25.00')
            per_km = Decimal('2.50')
            min_fare = Decimal('35.00')
            per_min = Decimal('0.50')
            currency = 'EUR'
        else:
            base_fare = rule.base_fare
            per_km = rule.per_km_rate
            min_fare = rule.minimum_fare
            per_min = rule.per_minute_rate
            currency = rule.currency

        distance_charge = (Decimal(str(distance_km)) * per_km).quantize(Decimal('0.01'))
        time_charge = (Decimal(str(duration_min or 0)) * per_min).quantize(Decimal('0.01'))
        
        raw_subtotal = base_fare + distance_charge + time_charge
        subtotal = max(min_fare, raw_subtotal)

        surcharge_amount = cls.get_applicable_surcharges(travel_dt)
        final_fare = subtotal + surcharge_amount

        return {
            'vehicle_class': vehicle_class.name,
            'currency': currency,
            'distance_km': float(distance_km),
            'duration_min': duration_min,
            'base_fare': base_fare,
            'distance_charge': distance_charge,
            'time_charge': time_charge,
            'subtotal': subtotal,
            'surcharge_amount': surcharge_amount,
            'final_fare': final_fare
        }

    @classmethod
    def calculate_hourly(
        cls,
        vehicle_class: VehicleClass,
        hours: int = 2,
        travel_dt: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculates hourly charter pricing.
        """
        rule = vehicle_class.pricing_rules.filter(is_active=True).first()
        hourly_rate = rule.hourly_rate if rule else Decimal('85.00')
        currency = rule.currency if rule else 'EUR'

        subtotal = (Decimal(str(hours)) * hourly_rate).quantize(Decimal('0.01'))
        surcharge_amount = cls.get_applicable_surcharges(travel_dt)
        final_fare = subtotal + surcharge_amount

        return {
            'vehicle_class': vehicle_class.name,
            'currency': currency,
            'hours': hours,
            'hourly_rate': hourly_rate,
            'subtotal': subtotal,
            'surcharge_amount': surcharge_amount,
            'final_fare': final_fare
        }

    @classmethod
    def calculate_fixed_route(
        cls,
        fixed_route: FixedRoute,
        is_return: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates flat-rate pricing for predefined fixed price transfer routes.
        Supports all transfer types: airport, city, hotel, resort, attraction, custom.
        """
        price = fixed_route.fixed_price
        if is_return and fixed_route.return_price:
            price = fixed_route.return_price

        return {
            'route_name': fixed_route.name,
            'transfer_type': fixed_route.transfer_type,
            'pickup_name': fixed_route.pickup_name,
            'dropoff_name': fixed_route.dropoff_name,
            'vehicle_class': fixed_route.vehicle_class.name,
            'currency': fixed_route.currency,
            'distance_km': float(fixed_route.distance_km),
            'estimated_duration_min': fixed_route.estimated_duration_min,
            'passenger_capacity': fixed_route.passenger_capacity,
            'luggage_capacity': fixed_route.luggage_capacity,
            'is_return': is_return,
            'final_fare': price
        }

