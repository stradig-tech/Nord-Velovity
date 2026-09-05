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
            from core.models import Enquiry, ContactSubmission
            from datetime import timedelta
            from django.utils import timezone
            import json

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

            # Dynamic 7-day velocity and inquiries
            now = timezone.now()
            today = now.date()
            days = [today - timedelta(days=i) for i in range(6, -1, -1)]
            chart_labels = [d.strftime('%a') for d in days]
            chart_bookings = []
            chart_inquiries = []

            for d in days:
                b_count = Booking.objects.filter(status__in=['CONFIRMED', 'COMPLETED'], created_at__date=d).count()
                i_count = Enquiry.objects.filter(created_at__date=d).count() + ContactSubmission.objects.filter(created_at__date=d).count()
                chart_bookings.append(b_count)
                chart_inquiries.append(i_count)

            total_7d_bookings = sum(chart_bookings)
            total_7d_inquiries = sum(chart_inquiries)

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
                'chart_labels': json.dumps(chart_labels),
                'chart_bookings': json.dumps(chart_bookings),
                'chart_inquiries': json.dumps(chart_inquiries),
                'total_7d_bookings': total_7d_bookings,
                'total_7d_inquiries': total_7d_inquiries,
            }
            if extra_context:
                custom_context.update(extra_context)
            return original_index(request, extra_context=custom_context)

        admin.site.index = luxury_admin_index
