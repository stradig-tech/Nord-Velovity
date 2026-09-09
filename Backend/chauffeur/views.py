from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Prefetch

from .models import (
    VehicleClass, Vehicle, FixedRoute, PricingRule,
    ChauffeurServiceStandard, ChauffeurInclusion, ChauffeurSafetyStandard
)
from .services import ChauffeurPricingService

def transport_home_view(request):
    """
    Renders the VIP Transport & Chauffeur hub page (transport.html).
    """
    vehicle_classes = VehicleClass.objects.filter(is_active=True).prefetch_related(
        'vehicles', 'pricing_rules', 'fixed_routes'
    ).order_by('sort_order')

    fixed_routes = FixedRoute.objects.filter(is_active=True).select_related('vehicle_class')[:6]

    context = {
        'vehicle_classes': vehicle_classes,
        'fixed_routes': fixed_routes,
    }
    return render(request, 'chauffeur/transport.html', context)


def vehicle_list_view(request):
    """
    Renders the luxury fleet catalog (cab-list.html) with search criteria & estimated pricing.
    """
    vehicles = Vehicle.objects.filter(is_active=True).select_related('vehicle_class').prefetch_related(
        'photos', 'vehicle_class__pricing_rules', 'vehicle_class__fixed_routes'
    )
    vehicle_classes = VehicleClass.objects.filter(is_active=True).order_by('sort_order')

    # Search Query Params
    class_slug = request.GET.get('class')
    pickup = request.GET.get('pickup', '').strip()
    drop = request.GET.get('drop', '').strip()
    date_str = request.GET.get('date', '').strip()
    time_str = request.GET.get('time', '').strip()
    trip_type = request.GET.get('trip_type', 'oneway')
    return_date = request.GET.get('return_date', '').strip()
    return_time = request.GET.get('return_time', '').strip()
    passengers = request.GET.get('passengers', '')

    if class_slug:
        vehicles = vehicles.filter(vehicle_class__slug=class_slug)
    if passengers and passengers.isdigit():
        vehicles = vehicles.filter(passenger_capacity__gte=int(passengers))

    is_roundtrip = trip_type == 'roundtrip'

    # Dynamic pricing calculations for each vehicle
    fare_estimates = {}
    for v in vehicles:
        rule = v.vehicle_class.pricing_rules.filter(is_active=True).first()
        if rule:
            # 25km standard airport / executive city transfer
            fare_calc = ChauffeurPricingService.calculate_point_to_point(
                vehicle_class=v.vehicle_class,
                distance_km=Decimal('25.0'),
                duration_min=30
            )
            estimated = fare_calc['final_fare']
            if is_roundtrip:
                estimated = (estimated * Decimal('1.85')).quantize(Decimal('0.01'))
            fare_estimates[v.id] = estimated
        else:
            fare_estimates[v.id] = Decimal('75.00') if not is_roundtrip else Decimal('138.75')

    context = {
        'vehicles': vehicles,
        'vehicle_classes': vehicle_classes,
        'selected_class': class_slug,
        'pickup': pickup,
        'drop': drop,
        'date': date_str,
        'time': time_str,
        'trip_type': trip_type,
        'return_date': return_date,
        'return_time': return_time,
        'passengers': passengers,
        'fare_estimates': fare_estimates,
        'is_roundtrip': is_roundtrip,
    }
    return render(request, 'chauffeur/cab-list.html', context)


def vehicle_detail_view(request, slug):
    """
    Renders the vehicle detail page (cab-details.html) with amenities and prefilled search params.
    """
    vehicle_class = get_object_or_404(
        VehicleClass.objects.prefetch_related(
            'vehicles__photos', 'pricing_rules', 'fixed_routes',
            'service_standards', 'inclusions', 'safety_standards', 'photos'
        ),
        slug=slug,
        is_active=True
    )

    # Specific vehicle if passed, else primary
    vehicle_id = request.GET.get('vehicle_id')
    primary_vehicle = None
    if vehicle_id and vehicle_id.isdigit():
        primary_vehicle = vehicle_class.vehicles.filter(id=int(vehicle_id), is_active=True).first()
    if not primary_vehicle:
        primary_vehicle = vehicle_class.vehicles.filter(is_active=True).first()

    pricing_rule = vehicle_class.pricing_rules.filter(is_active=True).first()
    fixed_routes = vehicle_class.fixed_routes.filter(is_active=True)

    pickup = request.GET.get('pickup', '').strip()
    drop = request.GET.get('drop', '').strip()
    date_str = request.GET.get('date', '').strip()
    time_str = request.GET.get('time', '').strip()
    trip_type = request.GET.get('trip_type', 'oneway')
    return_date = request.GET.get('return_date', '').strip()
    return_time = request.GET.get('return_time', '').strip()

    is_roundtrip = trip_type == 'roundtrip'
    fare_calc = ChauffeurPricingService.calculate_point_to_point(
        vehicle_class=vehicle_class,
        distance_km=Decimal('25.0'),
        duration_min=30
    )
    total_fare = fare_calc['final_fare']
    if is_roundtrip:
        total_fare = (total_fare * Decimal('1.85')).quantize(Decimal('0.01'))

    # Dynamic standards, inclusions, and safety standards (Class-specific with Global fallback)
    service_standards = list(vehicle_class.service_standards.filter(is_active=True).order_by('sort_order', 'id'))
    if not service_standards:
        service_standards = list(ChauffeurServiceStandard.objects.filter(vehicle_class__isnull=True, is_active=True).order_by('sort_order', 'id'))

    inclusions = list(vehicle_class.inclusions.filter(is_included=True, is_active=True).order_by('sort_order', 'id'))
    if not inclusions:
        inclusions = list(ChauffeurInclusion.objects.filter(vehicle_class__isnull=True, is_included=True, is_active=True).order_by('sort_order', 'id'))

    exclusions = list(vehicle_class.inclusions.filter(is_included=False, is_active=True).order_by('sort_order', 'id'))
    if not exclusions:
        exclusions = list(ChauffeurInclusion.objects.filter(vehicle_class__isnull=True, is_included=False, is_active=True).order_by('sort_order', 'id'))

    safety_standards = list(vehicle_class.safety_standards.filter(is_active=True).order_by('sort_order', 'id'))
    if not safety_standards:
        safety_standards = list(ChauffeurSafetyStandard.objects.filter(vehicle_class__isnull=True, is_active=True).order_by('sort_order', 'id'))

    # Cab photos: primary vehicle's photos, or class photos, or empty list
    cab_photos = []
    if primary_vehicle:
        cab_photos = list(primary_vehicle.photos.all().order_by('-is_primary', 'sort_order', 'id'))
    if not cab_photos:
        cab_photos = list(vehicle_class.photos.all().order_by('-is_primary', 'sort_order', 'id'))

    context = {
        'vehicle_class': vehicle_class,
        'vehicle': primary_vehicle,
        'pricing_rule': pricing_rule,
        'fixed_routes': fixed_routes,
        'pickup': pickup,
        'drop': drop,
        'date': date_str,
        'time': time_str,
        'trip_type': trip_type,
        'return_date': return_date,
        'return_time': return_time,
        'total_fare': total_fare,
        'is_roundtrip': is_roundtrip,
        'service_standards': service_standards,
        'inclusions': inclusions,
        'exclusions': exclusions,
        'safety_standards': safety_standards,
        'cab_photos': cab_photos,
    }
    return render(request, 'chauffeur/cab-details.html', context)


def chauffeur_booking_create_view(request, slug):
    """
    Handles form submission from cab-details.html and creates the Chauffeur reservation.
    """
    vehicle_class = get_object_or_404(VehicleClass, slug=slug, is_active=True)

    if request.method == 'POST':
        from django.contrib import messages
        from django.shortcuts import redirect
        from django.utils import timezone
        from datetime import datetime
        from accounts.models import CustomUser, CustomerProfile
        from bookings.services import BookingService

        # Vehicle
        vehicle_id = request.POST.get('vehicle_id')
        vehicle = None
        if vehicle_id and vehicle_id.isdigit():
            vehicle = vehicle_class.vehicles.filter(id=int(vehicle_id), is_active=True).first()
        if not vehicle:
            vehicle = vehicle_class.vehicles.filter(is_active=True).first()
        if not vehicle:
            messages.error(request, "Selected vehicle is currently unavailable.")
            return redirect('chauffeur:detail', slug=slug)

        # Customer account
        if request.user.is_authenticated:
            customer = request.user
        else:
            email = request.POST.get('email', '').strip().lower()
            full_name = request.POST.get('full_name', '').strip()
            phone = request.POST.get('phone', '').strip()

            if not email:
                messages.error(request, "Email address is required to book a chauffeur.")
                return redirect('chauffeur:detail', slug=slug)

            customer = CustomUser.objects.filter(email=email).first()
            if not customer:
                name_parts = full_name.split(' ', 1)
                first_name = name_parts[0] if name_parts else ''
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                base_user = email.split('@')[0]
                username = f"{base_user}_{CustomUser.objects.count()}"
                customer = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    role='CUSTOMER'
                )
                CustomerProfile.objects.create(user=customer)

        # Trip parameters
        pickup_address = request.POST.get('pickup_address', '').strip() or 'Helsinki-Vantaa Airport (HEL)'
        destination_address = request.POST.get('destination_address', '').strip() or 'Hotel Kämp, Helsinki'
        date_str = request.POST.get('date', '').strip()
        time_str = request.POST.get('time', '').strip()
        trip_type = request.POST.get('trip_type', 'oneway')
        is_return = trip_type == 'roundtrip'
        return_date_str = request.POST.get('return_date', '').strip()
        return_time_str = request.POST.get('return_time', '').strip()

        # Parse pickup_datetime
        try:
            if date_str and time_str:
                pickup_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            elif date_str:
                pickup_dt = datetime.strptime(date_str, "%Y-%m-%d")
            else:
                pickup_dt = timezone.now() + timezone.timedelta(days=1)
            pickup_datetime = timezone.make_aware(pickup_dt) if timezone.is_naive(pickup_dt) else pickup_dt
        except Exception:
            pickup_datetime = timezone.now() + timezone.timedelta(days=1)

        # Parse return_datetime
        return_datetime = None
        if is_return and return_date_str:
            try:
                r_time = return_time_str or "12:00"
                r_dt = datetime.strptime(f"{return_date_str} {r_time}", "%Y-%m-%d %H:%M")
                return_datetime = timezone.make_aware(r_dt) if timezone.is_naive(r_dt) else r_dt
            except Exception:
                pass

        special_requests = request.POST.get('special_requests', '').strip()
        quote_fare_str = request.POST.get('quote_fare', '').strip()
        quote_fare = Decimal(quote_fare_str) if quote_fare_str else None

        res = BookingService.create_chauffeur_booking(
            customer=customer,
            vehicle=vehicle,
            pickup_address=pickup_address,
            destination_address=destination_address,
            pickup_datetime=pickup_datetime,
            route_type='DISTANCE',
            passenger_count=vehicle.passenger_capacity,
            luggage_count=vehicle.luggage_capacity,
            is_return=is_return,
            return_pickup_address=destination_address if is_return else None,
            return_datetime=return_datetime,
            special_requests=special_requests,
            quote_fare=quote_fare
        )

        if res["success"]:
            return redirect('bookings:summary', booking_ref=res["booking_ref"])
        else:
            messages.error(request, res.get("error", "Failed to create chauffeur reservation."))
            return redirect('chauffeur:detail', slug=slug)

    return redirect('chauffeur:detail', slug=slug)


def api_calculate_chauffeur_fare(request):
    """
    JSON API endpoint for real-time chauffeur fare estimation.
    Supports point-to-point distance (km), hourly charter, and fixed route lookups.
    """
    fare_type = request.GET.get('type', 'distance') # distance, hourly, fixed
    class_id = request.GET.get('class_id')
    
    if not class_id:
        return JsonResponse({'success': False, 'error': 'Vehicle class is required'}, status=400)

    vehicle_class = get_object_or_404(VehicleClass, id=class_id)

    try:
        if fare_type == 'hourly':
            hours = int(request.GET.get('hours', 2))
            fare_data = ChauffeurPricingService.calculate_hourly(vehicle_class, hours)
        elif fare_type == 'fixed':
            route_id = request.GET.get('route_id')
            fixed_route = get_object_or_404(FixedRoute, id=route_id)
            is_return = request.GET.get('is_return', 'false').lower() == 'true'
            fare_data = ChauffeurPricingService.calculate_fixed_route(fixed_route, is_return)
        else: # distance-based
            distance_km = Decimal(str(request.GET.get('distance_km', 15.0)))
            duration_min = int(request.GET.get('duration_min', 20))
            fare_data = ChauffeurPricingService.calculate_point_to_point(
                vehicle_class=vehicle_class,
                distance_km=distance_km,
                duration_min=duration_min
            )

        return JsonResponse({'success': True, 'fare': fare_data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
