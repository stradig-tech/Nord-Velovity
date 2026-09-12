from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import CustomUser, CustomerProfile
from bookings.models import Booking
from tours.models import Tour, Wishlist

def login_view(request):
    """Handles customer login."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next') or 'accounts:dashboard'
            messages.success(request, f"Welcome back, {user.first_name or user.email}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password. Please try again.")

    return render(request, 'accounts/login.html')


def signup_view(request):
    """Handles new customer account registration."""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not email or not password:
            messages.error(request, "Email and password are required.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists. Please log in.")
        else:
            # Create unique username from email
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                role='CUSTOMER'
            )
            CustomerProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "Your account has been created successfully!")
            return redirect('accounts:dashboard')

    return render(request, 'accounts/signup.html')


def logout_view(request):
    """Logs out the customer and redirects to homepage."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


@login_required
def dashboard_view(request):
    """Customer overview dashboard & profile management."""
    user = request.user

    if request.method == 'POST':
        action = request.POST.get('action', 'update_profile')

        if action == 'update_profile':
            full_name = request.POST.get('full_name', '').strip()
            phone = request.POST.get('phone', '').strip()
            preferred_language = request.POST.get('preferred_language', 'en')

            if full_name:
                parts = full_name.split(' ', 1)
                user.first_name = parts[0]
                user.last_name = parts[1] if len(parts) > 1 else ''
            
            user.phone = phone

            # Handle Profile Picture (Avatar)
            if 'avatar' in request.FILES:
                avatar_file = request.FILES['avatar']
                if avatar_file.size > 5 * 1024 * 1024:
                    messages.error(request, "Image size exceeds 5MB limit.")
                    return redirect('accounts:dashboard')
                user.avatar = avatar_file
            elif request.POST.get('remove_avatar') == 'true':
                if user.avatar:
                    user.avatar.delete(save=False)
                    user.avatar = None

            user.save()

            profile, _ = CustomerProfile.objects.get_or_create(user=user)
            profile.preferred_language = preferred_language
            profile.save()

            messages.success(request, "Your profile has been updated successfully!")
            return redirect('accounts:dashboard')

        elif action == 'update_email':
            new_email = request.POST.get('new_email', '').strip().lower()
            if not new_email:
                messages.error(request, "Please enter a valid email address.")
            elif new_email == user.email:
                messages.info(request, "The entered email is already your current email address.")
            elif CustomUser.objects.filter(email=new_email).exclude(id=user.id).exists():
                messages.error(request, "An account with this email address already exists.")
            else:
                user.email = new_email
                user.save()
                messages.success(request, f"Your email address has been updated to {new_email}!")
            return redirect('accounts:dashboard')

        elif action == 'update_password':
            current_pwd = request.POST.get('current_password', '')
            new_pwd = request.POST.get('new_password', '')
            confirm_pwd = request.POST.get('confirm_password', '')

            if not user.check_password(current_pwd):
                messages.error(request, "Current password does not match.")
            elif len(new_pwd) < 6:
                messages.error(request, "New password must be at least 6 characters.")
            elif new_pwd != confirm_pwd:
                messages.error(request, "New password confirmation does not match.")
            else:
                from django.contrib.auth import update_session_auth_hash
                user.set_password(new_pwd)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password has been changed successfully!")
            return redirect('accounts:dashboard')

    bookings = Booking.objects.filter(customer=user).order_by('-created_at')
    
    total_bookings = bookings.count()
    confirmed_bookings = bookings.filter(status='CONFIRMED').count()
    pending_bookings = bookings.filter(status='PENDING').count()
    wishlist_count = Wishlist.objects.filter(user=user).count()
    customer_profile = getattr(user, 'customer_profile', None)

    context = {
        'recent_bookings': bookings[:5],
        'total_bookings': total_bookings,
        'confirmed_bookings': confirmed_bookings,
        'pending_bookings': pending_bookings,
        'wishlist_count': wishlist_count,
        'preferred_language': customer_profile.preferred_language if customer_profile else 'en',
    }
    if request.headers.get('HX-Request'):
        return render(request, 'accounts/partials/dashboard_profile_partial.html', context)
    return render(request, 'accounts/user-dashboard.html', context)


@login_required
def my_bookings_view(request):
    """List of all customer bookings."""
    bookings = Booking.objects.filter(customer=request.user).select_related(
        'tour_booking__tour', 'chauffeur_booking__vehicle__vehicle_class'
    ).order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter.upper())

    context = {
        'bookings': bookings,
        'selected_status': status_filter,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'accounts/partials/my_bookings_partial.html', context)
    return render(request, 'accounts/my-bookings.html', context)


@login_required
def booking_order_detail_view(request, booking_ref):
    """
    Renders the customer's full tour/chauffeur order details:
    - Booking reference, status lifecycle, and timeline
    - How the tour occurs: dates, meeting points, duration, vehicle, day-by-day itinerary, inclusions
    - Guest information and special requests
    - Payment breakdown, payment method, settlement status, and receipt
    """
    booking = get_object_or_404(
        Booking.objects.select_related(
            'customer',
            'coupon',
            'tour_booking__tour__destination__country',
            'tour_booking__tour_date',
            'tour_booking__departure',
            'tour_booking__vehicle_type',
            'chauffeur_booking__vehicle__vehicle_class',
        ).prefetch_related(
            'tour_booking__tour__media',
            'tour_booking__tour__highlights',
            'tour_booking__tour__itinerary',
            'tour_booking__tour__inclusions',
            'tour_booking__tour__pickups',
            'tour_booking__guests',
            'chauffeur_booking__vehicle__photos',
            'status_logs',
        ),
        booking_ref=booking_ref
    )

    # Security: Ensure only the booking owner or staff can view
    if booking.customer != request.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to view this booking order.")
        return redirect('accounts:my_bookings')

    tour_booking = getattr(booking, 'tour_booking', None)
    chauffeur_booking = getattr(booking, 'chauffeur_booking', None)
    tour = tour_booking.tour if tour_booking else None

    context = {
        'booking': booking,
        'tour_booking': tour_booking,
        'chauffeur_booking': chauffeur_booking,
        'tour': tour,
        'active_tab': 'bookings',
    }

    if request.headers.get('HX-Request'):
        return render(request, 'accounts/partials/booking_order_detail_partial.html', context)
    return render(request, 'accounts/booking-order-detail.html', context)


@login_required
def my_wishlist_view(request):
    """List of tours saved to customer's wishlist."""
    wishlists = Wishlist.objects.filter(user=request.user).select_related(
        'tour__destination__country'
    ).prefetch_related('tour__pricing', 'tour__media').order_by('-created_at')

    context = {
        'wishlists': wishlists,
        'active_tab': 'wishlist',
    }
    if request.headers.get('HX-Request'):
        return render(request, 'accounts/partials/my_wishlist_partial.html', context)
    return render(request, 'accounts/my-wishlist.html', context)


@login_required
def payment_details_view(request):
    """Customer payment methods & VIP card management."""
    context = {'active_tab': 'payment'}
    if request.headers.get('HX-Request'):
        return render(request, 'accounts/partials/payment_details_partial.html', context)
    return render(request, 'accounts/payment-details.html', context)


@require_POST
def api_toggle_wishlist(request, tour_id):
    """AJAX endpoint to add/remove a tour from the customer's wishlist."""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'login_required': True,
            'login_url': f"/accounts/login/?next={request.META.get('HTTP_REFERER', '/tours/')}",
            'message': "Please log in to save tours to your wishlist."
        }, status=401)

    tour = get_object_or_404(Tour, id=tour_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, tour=tour).first()

    if wishlist_item:
        wishlist_item.delete()
        is_saved = False
        message = f"Removed '{tour.title}' from your wishlist."
    else:
        Wishlist.objects.create(user=request.user, tour=tour)
        is_saved = True
        message = f"Saved '{tour.title}' to your wishlist!"

    return JsonResponse({
        'success': True,
        'is_saved': is_saved,
        'message': message,
        'count': Wishlist.objects.filter(user=request.user).count()
    })


@login_required
def settings_view(request):
    """Account settings to update personal details."""
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.phone = request.POST.get('phone', user.phone).strip()
        user.save()
        messages.success(request, "Your profile has been updated successfully!")
        return redirect('accounts:settings')

    context = {'user': user}
    if request.headers.get('HX-Request'):
        return render(request, 'accounts/partials/settings_partial.html', context)
    return render(request, 'accounts/settings.html', context)

