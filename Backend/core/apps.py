from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from django.contrib import admin
        from decimal import Decimal
        from django.db.models import Sum

        original_index = admin.site.index

        def luxury_admin_index(request, extra_context=None):
            from tours.models import Tour, TourReview
            from chauffeur.models import Vehicle
            from bookings.models import Booking
            from accounts.models import CustomUser

            total_tours = Tour.objects.count()
            total_income = Booking.objects.filter(
                status__in=['CONFIRMED', 'COMPLETED']
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            total_vehicles = Vehicle.objects.count()
            total_bookings = Booking.objects.count()
            pending_bookings = Booking.objects.filter(status='PENDING').count()
            confirmed_bookings = Booking.objects.filter(status='CONFIRMED').count()
            
            popular_tours = Tour.objects.filter(status='PUBLISHED').prefetch_related('media', 'pricing', 'destination')[:4]
            recent_bookings = Booking.objects.select_related(
                'customer', 'tour_booking__tour', 'chauffeur_booking__vehicle'
            ).order_by('-created_at')[:8]

            recent_arrivals = Booking.objects.filter(
                status='CONFIRMED'
            ).select_related('customer', 'tour_booking__tour').order_by('-created_at')[:4]
            recent_reviews = TourReview.objects.select_related('tour', 'user').order_by('-created_at')[:4]

            custom_context = {
                'total_tours': total_tours,
                'total_income': total_income,
                'total_vehicles': total_vehicles,
                'total_bookings': total_bookings,
                'pending_bookings': pending_bookings,
                'confirmed_bookings': confirmed_bookings,
                'popular_tours': popular_tours,
                'recent_bookings': recent_bookings,
                'recent_arrivals': recent_arrivals,
                'recent_reviews': recent_reviews,
            }
            if extra_context:
                custom_context.update(extra_context)
            return original_index(request, extra_context=custom_context)

        admin.site.index = luxury_admin_index
