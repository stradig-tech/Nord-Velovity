from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Booking, TourBooking
from tours.models import Tour, TourDate
from accounts.models import CustomUser, CustomerProfile
from .services import BookingService
from payments.services import CouponService
from tours.services import TourPricingService

def booking_create_view(request, tour_slug):
    """
    Renders the reservation form (tour-booking.html) to collect guest details before checkout.
    """
    tour = get_object_or_404(Tour.objects.prefetch_related('dates', 'pricing'), slug=tour_slug, status='PUBLISHED')
    available_dates = tour.dates.filter(status='AVAILABLE').order_by('start_date')

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

        date_id = request.POST.get('date_id')
        tour_date = TourDate.objects.filter(id=date_id, tour=tour, status='AVAILABLE').first()
        if not tour_date:
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

    initial_date_id = request.GET.get('date_id')
    try:
        initial_adults = max(1, int(request.GET.get('adults', 2)))
    except (ValueError, TypeError):
        initial_adults = 2
    try:
        initial_children = max(0, int(request.GET.get('children', 0)))
    except (ValueError, TypeError):
        initial_children = 0

    selected_date = None
    if initial_date_id:
        selected_date = available_dates.filter(id=initial_date_id).first()
    if not selected_date and available_dates.exists():
        selected_date = available_dates.first()

    pricing = None
    try:
        pricing = TourPricingService.calculate_price(
            tour=tour,
            tour_date=selected_date,
            adults=initial_adults,
            children=initial_children
        )
    except Exception:
        pass

    context = {
        'tour': tour,
        'available_dates': available_dates,
        'selected_date': selected_date,
        'initial_adults': initial_adults,
        'initial_children': initial_children,
        'pricing': pricing,
    }
    return render(request, 'tour-booking.html', context)


def booking_summary_view(request, booking_ref):
    """
    Renders the pre-checkout review page (booking-summary.html) with coupon application and Stripe button.
    """
    booking = get_object_or_404(
        Booking.objects.select_related(
            'tour_booking__tour',
            'tour_booking__tour_date',
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
    return render(request, 'booking-summary.html', context)


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

    return render(request, 'booking-success.html', {
        'booking': booking,
        'tour_booking': getattr(booking, 'tour_booking', None) if booking else None,
        'chauffeur_booking': getattr(booking, 'chauffeur_booking', None) if booking else None,
        'ref': booking_ref,
        'method': method_param,
    })
