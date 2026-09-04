from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q
from django.contrib import messages

from bookings.models import Booking
from tours.models import Tour, TourReview
from accounts.models import CustomUser

@staff_member_required
def admin_dashboard_view(request):
    """Custom luxury executive dashboard overview."""
    total_bookings = Booking.objects.count()
    confirmed_bookings = Booking.objects.filter(status='CONFIRMED').count()
    
    total_revenue = Booking.objects.filter(
        status__in=['CONFIRMED', 'COMPLETED']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    active_tours = Tour.objects.filter(status='PUBLISHED').count()
    total_guests = CustomUser.objects.filter(role='CUSTOMER').count()

    recent_bookings = Booking.objects.select_related(
        'customer', 'tour_booking__tour', 'chauffeur_booking__vehicle_class'
    ).order_by('-created_at')[:8]

    context = {
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'total_revenue': total_revenue,
        'active_tours': active_tours,
        'total_guests': total_guests,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'admin-dashboard.html', context)


@staff_member_required
def admin_bookings_view(request):
    """Custom bookings management list."""
    bookings = Booking.objects.select_related(
        'customer', 'tour_booking__tour', 'chauffeur_booking__vehicle_class'
    ).order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter.upper())

    return render(request, 'admin-bookings.html', {'bookings': bookings, 'selected_status': status_filter})


@staff_member_required
def admin_booking_detail_view(request, booking_ref):
    """Custom booking detail view."""
    booking = get_object_or_404(
        Booking.objects.select_related('customer', 'tour_booking__tour', 'chauffeur_booking__vehicle_class'),
        booking_ref=booking_ref
    )
    return render(request, 'admin-booking-detail.html', {'booking': booking})


@staff_member_required
def admin_guests_view(request):
    """Custom guests / customers management list."""
    guests = CustomUser.objects.filter(role='CUSTOMER').annotate(
        booking_count=Count('bookings')
    ).order_by('-date_joined')
    return render(request, 'admin-guest-list.html', {'guests': guests})


@staff_member_required
def admin_guest_detail_view(request, guest_id):
    """Customer profile and booking history detail."""
    guest = get_object_or_404(CustomUser, id=guest_id)
    guest_bookings = Booking.objects.filter(customer=guest).order_by('-created_at')
    return render(request, 'admin-guest-detail.html', {'guest': guest, 'bookings': guest_bookings})


@staff_member_required
def admin_reviews_view(request):
    """Custom reviews moderation."""
    reviews = TourReview.objects.select_related('tour', 'user').order_by('-created_at')
    
    # Quick approval action
    if request.method == 'POST' and 'toggle_review_id' in request.POST:
        r_id = request.POST.get('toggle_review_id')
        review = get_object_or_404(TourReview, id=r_id)
        review.is_approved = not review.is_approved
        review.save()
        messages.success(request, f"Review status updated for {review.user.email}!")
        return redirect('custom_admin:reviews')

    return render(request, 'admin-reviews.html', {'reviews': reviews})


@staff_member_required
def admin_earnings_view(request):
    """Earnings, revenue breakdown, and financial reports."""
    revenue_by_type = Booking.objects.filter(
        status__in=['CONFIRMED', 'COMPLETED']
    ).values('booking_type').annotate(total=Sum('total_amount'), count=Count('id'))

    total_revenue = Booking.objects.filter(
        status__in=['CONFIRMED', 'COMPLETED']
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    return render(request, 'admin-earnings.html', {
        'revenue_by_type': revenue_by_type,
        'total_revenue': total_revenue
    })


@staff_member_required
def admin_settings_view(request):
    """Executive platform configuration settings."""
    return render(request, 'admin-settings.html')
