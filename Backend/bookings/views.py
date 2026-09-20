from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Booking, TourBooking
from tours.models import Tour, TourDate, Departure, DepartureCapacity, VehicleType
from accounts.models import CustomUser, CustomerProfile
from .services import BookingService
from payments.services import CouponService
from tours.services import TourPricingService, DepartureService

def booking_create_view(request, tour_slug):
    """
    Renders the reservation form (tour-booking.html) to collect guest details before checkout.
    Supports Departure-based bookings with multi-capacity vehicle types (Private Car, Micro, Group Bus).
    """
    tour = get_object_or_404(
        Tour.objects.prefetch_related('departures__capacities__vehicle_type', 'pricing', 'option_pricing'),
        slug=tour_slug,
        status='PUBLISHED'
    )
    available_departures = tour.departures.filter(status='OPEN').prefetch_related('capacities__vehicle_type').order_by('date', 'time')
    available_dates = tour.dates.filter(status='AVAILABLE').order_by('start_date')
    vehicle_types = VehicleType.objects.filter(is_active=True).order_by('sort_order', 'default_capacity')

    if request.method == 'POST':
        # Customer details
        if request.user.is_authenticated:
            customer = request.user
        else:
            email = request.POST.get('email', '').strip().lower()
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone = request.POST.get('phone', '').strip()

            if not email:
                messages.error(request, "Email address is required to make a booking.")
                return redirect('bookings:create', tour_slug=tour.slug)

            # Find or create guest customer account
            customer = CustomUser.objects.filter(email=email).first()
            if not customer:
                username = email.split('@')[0] + '_' + CustomUser.objects.count().__str__()
                customer = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone,
                    role='CUSTOMER'
                )
                CustomerProfile.objects.create(user=customer)

        departure_id = request.POST.get('departure_id')
        date_id = request.POST.get('date_id')
        vehicle_type_id = request.POST.get('vehicle_type_id')

        departure = None
        tour_date = None
        vehicle_type = None

        if departure_id:
            if str(departure_id).startswith('date_'):
                date_id = str(departure_id).replace('date_', '')
                departure_id = None
            else:
                departure = Departure.objects.filter(id=departure_id, tour=tour).first()

        if date_id and not departure:
            tour_date = TourDate.objects.filter(id=date_id, tour=tour).first()
            if tour_date:
                departure = Departure.objects.filter(tour=tour, date=tour_date.start_date).first()
                if not departure:
                    default_time = getattr(tour_date, 'start_time', None) or '09:00'
                    departure = Departure.objects.create(
                        tour=tour,
                        date=tour_date.start_date,
                        time=default_time,
                        status='OPEN'
                    )
                    departure.auto_init_capacities()

        if vehicle_type_id:
            vehicle_type = VehicleType.objects.filter(id=vehicle_type_id, is_active=True).first()
        if not vehicle_type:
            vehicle_type = VehicleType.objects.filter(slug='micro').first() or vehicle_types.first()

        if not departure and not tour_date:
            messages.error(request, "Please select an available departure date.")
            return redirect('bookings:create', tour_slug=tour.slug)

        adults = int(request.POST.get('adults', 1))
        children = int(request.POST.get('children', 0))
        special_requests = request.POST.get('special_requests', '')
        dietary_requirements = request.POST.get('dietary_requirements', '')
        customer_notes = request.POST.get('customer_notes', '')

        # Build guest list
        guests_info = []
        for i in range(1, adults + 1):
            name = request.POST.get(f'guest_adult_{i}_name', f"Adult Guest {i}")
            guests_info.append({'full_name': name, 'guest_type': 'ADULT'})
        for i in range(1, children + 1):
            name = request.POST.get(f'guest_child_{i}_name', f"Child Guest {i}")
            guests_info.append({'full_name': name, 'guest_type': 'CHILD'})

        result = BookingService.create_tour_booking(
            customer=customer,
            tour=tour,
            tour_date=tour_date,
            departure=departure,
            vehicle_type=vehicle_type,
            adults=adults,
            children=children,
            guests_info=guests_info,
            special_requests=special_requests,
            dietary_requirements=dietary_requirements,
            customer_notes=customer_notes
        )

        if result['success']:
            return redirect('bookings:summary', booking_ref=result['booking_ref'])
        else:
            messages.error(request, result.get('error', 'Booking could not be created.'))

    initial_departure_id = request.GET.get('departure_id')
    initial_date_id = request.GET.get('date_id')
    initial_vehicle_id = request.GET.get('vehicle_type_id') or request.GET.get('vehicle_type')

    try:
        initial_adults = max(1, int(request.GET.get('adults', 2)))
    except (ValueError, TypeError):
        initial_adults = 2
    try:
        initial_children = max(0, int(request.GET.get('children', 0)))
    except (ValueError, TypeError):
        initial_children = 0

    selected_departure = None
    if initial_departure_id:
        selected_departure = available_departures.filter(id=initial_departure_id).first()
    elif initial_date_id:
        td = available_dates.filter(id=initial_date_id).first()
        if td:
            selected_departure = available_departures.filter(date=td.start_date).first()

    if not selected_departure and available_departures.exists():
        selected_departure = available_departures.first()

    selected_vehicle_type = None
    if initial_vehicle_id:
        selected_vehicle_type = (
            vehicle_types.filter(id=initial_vehicle_id).first() or
            vehicle_types.filter(slug=initial_vehicle_id).first()
        )
    if not selected_vehicle_type:
        selected_vehicle_type = vehicle_types.filter(slug='micro').first() or vehicle_types.first()

    # Calculate pricing
    pricing = None
    try:
        if selected_departure and selected_vehicle_type:
            dc = selected_departure.capacities.filter(vehicle_type=selected_vehicle_type).first()
            pricing = DepartureService.calculate_price(
                tour=tour,
                vehicle_type=selected_vehicle_type,
                departure_capacity=dc,
                adults=initial_adults,
                children=initial_children
            )
        elif available_dates.exists():
            pricing = TourPricingService.calculate_price(
                tour=tour,
                tour_date=available_dates.first(),
                adults=initial_adults,
                children=initial_children
            )
    except Exception:
        pass

    context = {
        'tour': tour,
        'available_departures': available_departures,
        'available_dates': available_dates,
        'vehicle_types': vehicle_types,
        'selected_departure': selected_departure,
        'selected_vehicle_type': selected_vehicle_type,
        'selected_date': selected_departure.date if selected_departure else (available_dates.first().start_date if available_dates.exists() else None),
        'initial_adults': initial_adults,
        'initial_children': initial_children,
        'pricing': pricing,
    }
    return render(request, 'bookings/tour-booking.html', context)


def booking_summary_view(request, booking_ref):
    """
    Renders the pre-checkout review page (booking-summary.html) with coupon application and Stripe button.
    """
    booking = get_object_or_404(
        Booking.objects.select_related(
            'tour_booking__tour',
            'tour_booking__tour_date',
            'tour_booking__departure',
            'tour_booking__vehicle_type',
            'chauffeur_booking__vehicle__vehicle_class',
            'customer',
            'coupon'
        ),
        booking_ref=booking_ref
    )

    # Handle coupon application
    if request.method == 'POST' and 'apply_coupon' in request.POST:
        coupon_code = request.POST.get('coupon_code', '').strip()
        service_type = 'CHAUFFEUR' if booking.booking_type == 'CHAUFFEUR' else 'TOUR'
        coupon_res = CouponService.validate_coupon(
            coupon_code=coupon_code,
            order_amount=booking.subtotal,
            user=booking.customer,
            service_type=service_type
        )

        if coupon_res['valid']:
            booking.coupon = coupon_res['coupon']
            booking.discount_amount = coupon_res['discount_amount']
            booking.total_amount = coupon_res['final_amount']
            booking.save(update_fields=['coupon', 'discount_amount', 'total_amount'])
            messages.success(request, f"Coupon '{coupon_code}' applied successfully! You saved €{coupon_res['discount_amount']}.")
        else:
            messages.error(request, coupon_res['error'])

    context = {
        'booking': booking,
        'tour_booking': getattr(booking, 'tour_booking', None),
        'chauffeur_booking': getattr(booking, 'chauffeur_booking', None),
    }
    return render(request, 'bookings/booking-summary.html', context)


def booking_success_view(request):
    """
    Renders the order confirmation page (booking-success.html) after payment completion or offline confirmation.
    """
    booking_ref = request.GET.get('ref')
    method_param = request.GET.get('method', 'stripe')
    booking = None
    if booking_ref:
        booking = Booking.objects.select_related(
            'customer',
            'tour_booking__tour',
            'tour_booking__tour_date',
            'chauffeur_booking__vehicle__vehicle_class'
        ).filter(booking_ref=booking_ref).first()

    return render(request, 'bookings/booking-success.html', {
        'booking': booking,
        'tour_booking': getattr(booking, 'tour_booking', None) if booking else None,
        'chauffeur_booking': getattr(booking, 'chauffeur_booking', None) if booking else None,
        'ref': booking_ref,
        'method': method_param,
    })
