import json
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

from tours.models import Tour, Departure, DepartureCapacity, VehicleType, TourOptionPricing
from tours.services import DepartureService
from bookings.models import Booking, TourBooking, GuaranteedReattempt
from bookings.services import BookingService
from accounts.models import CustomUser, CustomerProfile


@staff_member_required
def departure_calendar_view(request):
    """
    Renders the central departure & capacity calendar in the admin dashboard.
    Visualizes per-departure capacity across Private Car (4), Micro (12), and Group Bus (54).
    """
    tours = Tour.objects.filter(status='PUBLISHED').order_by('title')
    vehicle_types = VehicleType.objects.filter(is_active=True).order_by('sort_order', 'default_capacity')

    # Selected tour filter (optional)
    tour_id = request.GET.get('tour_id')
    selected_tour = None
    if tour_id:
        selected_tour = Tour.objects.filter(id=tour_id).first()

    context = {
        'title': 'Central Departure & Capacity Calendar',
        'tours': tours,
        'selected_tour': selected_tour,
        'vehicle_types': vehicle_types,
    }
    return render(request, 'admin/departure_calendar.html', context)


@staff_member_required
@require_GET
def departure_calendar_api(request):
    """
    API returning departure events with multi-capacity breakdown for FullCalendar / Month view.
    Params:
        start: YYYY-MM-DD
        end: YYYY-MM-DD
        tour_id: int (optional)
        status: string (optional)
    """
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')
    tour_id = request.GET.get('tour_id')
    status_filter = request.GET.get('status')

    qs = Departure.objects.select_related('tour').prefetch_related('capacities__vehicle_type')

    if start_str:
        try:
            start_date = datetime.strptime(start_str[:10], '%Y-%m-%d').date()
            qs = qs.filter(date__gte=start_date)
        except ValueError:
            pass

    if end_str:
        try:
            end_date = datetime.strptime(end_str[:10], '%Y-%m-%d').date()
            qs = qs.filter(date__lte=end_date)
        except ValueError:
            pass

    if tour_id:
        qs = qs.filter(tour_id=tour_id)

    if status_filter:
        qs = qs.filter(status=status_filter.upper())

    events = []
    for dep in qs:
        capacities_data = []
        total_sellable = 0
        total_seats = 0
        total_booked = 0

        for c in dep.capacities.all():
            sellable = c.public_sellable
            total_sellable += sellable
            total_seats += c.total_capacity
            total_booked += c.booked_count

            capacities_data.append({
                'capacity_id': c.id,
                'vehicle_type': c.vehicle_type.name,
                'vehicle_slug': c.vehicle_type.slug,
                'vehicle_icon': c.vehicle_type.icon or '🚗',
                'total': c.total_capacity,
                'booked': c.booked_count,
                'blocked': c.blocked_seats,
                'reattempt_reserved': c.reattempt_reserved,
                'sellable': sellable,
                'is_sold_out': c.is_sold_out,
                'price_override_adult': str(c.price_override_adult) if c.price_override_adult else None,
                'price_override_child': str(c.price_override_child) if c.price_override_child else None,
            })

        # Determine display color based on status and capacity
        if dep.status == 'BLOCKED' or dep.status == 'CLOSED':
            color = '#EF4444' # red
        elif dep.status == 'SOLD_OUT' or total_sellable <= 0:
            color = '#F97316' # orange
        elif dep.status == 'OPERATIONALLY_RESERVED':
            color = '#8B5CF6' # purple
        else:
            color = '#10B981' # emerald green

        events.append({
            'id': dep.id,
            'tour_id': dep.tour_id,
            'tour_title': dep.tour.title,
            'title': f"{dep.tour.title} ({dep.time.strftime('%H:%M')})",
            'start': f"{dep.date.strftime('%Y-%m-%d')}T{dep.time.strftime('%H:%M:%S')}",
            'date': dep.date.strftime('%Y-%m-%d'),
            'time': dep.time.strftime('%H:%M'),
            'status': dep.status,
            'status_display': dep.get_status_display(),
            'color': color,
            'total_sellable': total_sellable,
            'total_seats': total_seats,
            'total_booked': total_booked,
            'capacities': capacities_data,
            'notes': dep.notes,
        })

    return JsonResponse({'events': events})


@staff_member_required
@require_POST
def departure_status_toggle_api(request, departure_id):
    """
    One-click admin action to switch status: OPEN, CLOSED, BLOCKED, or OPERATIONALLY_RESERVED.
    """
    departure = get_object_or_404(Departure, id=departure_id)
    try:
        data = json.loads(request.body.decode('utf-8'))
        new_status = data.get('status', 'OPEN').upper()
    except Exception:
        new_status = request.POST.get('status', 'OPEN').upper()

    valid_statuses = dict(Departure.STATUS_CHOICES)
    if new_status not in valid_statuses:
        return JsonResponse({'success': False, 'error': f'Invalid status: {new_status}'}, status=400)

    departure.status = new_status
    departure.save(update_fields=['status', 'updated_at'])
    return JsonResponse({
        'success': True,
        'departure_id': departure.id,
        'new_status': new_status,
        'status_display': departure.get_status_display()
    })


@staff_member_required
@require_POST
def departure_capacity_update_api(request, departure_id):
    """
    Updates individual vehicle capacity on a departure: total_capacity, blocked_seats, or price overrides.
    """
    departure = get_object_or_404(Departure, id=departure_id)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    capacity_id = data.get('capacity_id')
    capacity = get_object_or_404(DepartureCapacity, id=capacity_id, departure=departure)

    if 'total_capacity' in data and data['total_capacity'] is not None:
        capacity.total_capacity = max(0, int(data['total_capacity']))

    if 'blocked_seats' in data and data['blocked_seats'] is not None:
        capacity.blocked_seats = max(0, int(data['blocked_seats']))

    if 'price_override_adult' in data:
        val = data['price_override_adult']
        capacity.price_override_adult = Decimal(str(val)) if val else None

    if 'price_override_child' in data:
        val = data['price_override_child']
        capacity.price_override_child = Decimal(str(val)) if val else None

    capacity.save()

    return JsonResponse({
        'success': True,
        'capacity_id': capacity.id,
        'public_sellable': capacity.public_sellable,
        'is_sold_out': capacity.is_sold_out,
    })


@staff_member_required
def admin_manual_booking_view(request):
    """
    Dedicated admin interface to book tours for Phone, Hotel Concierge, or Walk-in guests.
    Directly attributes to MANUAL or HOTEL_AGENT channel and deducts from central capacity.
    """
    tours = Tour.objects.filter(status='PUBLISHED').order_by('title')
    vehicle_types = VehicleType.objects.filter(is_active=True).order_by('sort_order', 'default_capacity')

    if request.method == 'POST':
        tour_id = request.POST.get('tour_id')
        departure_id = request.POST.get('departure_id')
        vehicle_type_id = request.POST.get('vehicle_type_id')
        channel_source = request.POST.get('source', 'MANUAL')
        external_ref = request.POST.get('external_reference', '').strip()

        guest_email = request.POST.get('email', '').strip().lower()
        guest_name = request.POST.get('name', '').strip()
        guest_phone = request.POST.get('phone', '').strip()
        adults = int(request.POST.get('adults', 1))
        children = int(request.POST.get('children', 0))
        customer_notes = request.POST.get('customer_notes', '')

        tour = get_object_or_404(Tour, id=tour_id)
        departure = get_object_or_404(Departure, id=departure_id, tour=tour)
        vehicle_type = get_object_or_404(VehicleType, id=vehicle_type_id)

        # Customer find or create
        customer = CustomUser.objects.filter(email=guest_email).first()
        if not customer:
            name_parts = guest_name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            username = (guest_email.split('@')[0] if guest_email else 'agent_booking') + '_' + str(CustomUser.objects.count() + 1)
            customer = CustomUser.objects.create_user(
                username=username,
                email=guest_email or f"manual_{username}@nordvelocity.local",
                first_name=first_name,
                last_name=last_name,
                phone=guest_phone,
                role='CUSTOMER'
            )
            CustomerProfile.objects.create(user=customer)

        result = BookingService.create_tour_booking(
            customer=customer,
            tour=tour,
            departure=departure,
            vehicle_type=vehicle_type,
            adults=adults,
            children=children,
            source=channel_source,
            external_reference=external_ref,
            status='CONFIRMED', # Manual agent bookings are confirmed immediately
            customer_notes=customer_notes
        )

        if result['success']:
            messages.success(request, f"Manual booking {result['booking_ref']} created successfully on {departure} via {vehicle_type.name}.")
            return redirect('/admin/bookings/booking/')
        else:
            messages.error(request, f"Failed to create manual booking: {result.get('error')}")

    return render(request, 'admin/manual_booking_form.html', {
        'title': 'Create Manual Agent / Phone Booking',
        'tours': tours,
        'vehicle_types': vehicle_types,
    })


@staff_member_required
@require_POST
def admin_rebook_departure_api(request, booking_id):
    """
    API to move a tour booking from one departure to another.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    new_departure_id = data.get('new_departure_id')
    new_vehicle_type_id = data.get('new_vehicle_type_id')
    reason = data.get('reason', 'Admin moved booking')

    new_departure = get_object_or_404(Departure, id=new_departure_id)
    new_vt = VehicleType.objects.filter(id=new_vehicle_type_id).first() if new_vehicle_type_id else None

    result = BookingService.rebook_departure(
        booking=booking,
        new_departure=new_departure,
        new_vehicle_type=new_vt,
        changed_by=request.user,
        reason=reason
    )

    if result['success']:
        return JsonResponse({'success': True, 'booking_ref': booking.booking_ref, 'new_departure': str(new_departure)})
    return JsonResponse({'success': False, 'error': result['error']}, status=400)
