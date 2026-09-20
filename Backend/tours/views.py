import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Min, Count, Prefetch

from .models import (
    Country, Tour, Destination, Season, ExperienceType, TravelStyle, 
    TourCategory, TourDate, TourPricing, Departure, DepartureCapacity,
    VehicleType, TourOptionPricing
)
from .services import TourPricingService, DepartureService
from core.models import Enquiry

def tour_list_view(request):
    """
    Renders the tour package catalog with dynamic filtering by country, destination, style, and keyword.
    """
    tours = Tour.objects.filter(status='PUBLISHED').prefetch_related(
        'pricing', 'destination', 'destination__country', 'media', 'seasons', 'experience_types'
    )

    # Country filter
    country_slug = request.GET.get('country')
    dest_slug = request.GET.get('destination')
    category_slug = request.GET.get('category')
    style_slug = request.GET.get('style')
    search_query = request.GET.get('q', '').strip()

    # If search_query matches a country directly and no explicit country_slug was set
    if search_query and not country_slug:
        matched_country_q = Country.objects.filter(is_active=True).filter(
            Q(name__iexact=search_query) | Q(slug__iexact=search_query)
        ).first()
        if matched_country_q:
            country_slug = matched_country_q.slug

    if country_slug:
        tours = tours.filter(destination__country__slug=country_slug)

    # Destination filter
    if dest_slug:
        tours = tours.filter(destination__slug=dest_slug)

    # Category / Experience filter
    if category_slug:
        tours = tours.filter(experience_types__slug=category_slug)

    # Travel Style filter
    if style_slug:
        tours = tours.filter(travel_style__slug=style_slug)

    # Search Query
    if search_query:
        tours = tours.filter(
            Q(title__icontains=search_query) |
            Q(short_summary__icontains=search_query) |
            Q(overview__icontains=search_query) |
            Q(destination__name__icontains=search_query) |
            Q(destination__country__name__icontains=search_query) |
            Q(destination__country__slug__icontains=search_query)
        )

    # Resolve Active Destination Locations for the search
    matched_country = None
    country_destinations = []
    selected_dest_obj = None

    if dest_slug:
        selected_dest_obj = Destination.objects.filter(slug=dest_slug, is_active=True).select_related('country').annotate(
            tour_count=Count('tours', filter=Q(tours__status='PUBLISHED'))
        ).first()
        if selected_dest_obj and selected_dest_obj.country:
            matched_country = selected_dest_obj.country

    if country_slug and not matched_country:
        matched_country = Country.objects.filter(slug=country_slug, is_active=True).first()

    if matched_country:
        country_destinations = list(matched_country.destinations.filter(is_active=True).annotate(
            tour_count=Count('tours', filter=Q(tours__status='PUBLISHED'))
        ).order_by('sort_order', '-tour_count', 'name'))
    elif search_query:
        # Match active destinations by name or country name for general search
        matched_dests = list(Destination.objects.filter(is_active=True).filter(
            Q(name__icontains=search_query) | Q(country__name__icontains=search_query)
        ).select_related('country').annotate(
            tour_count=Count('tours', filter=Q(tours__status='PUBLISHED'))
        ).order_by('sort_order', '-tour_count', 'name'))
        if matched_dests:
            country_destinations = matched_dests

    # Sorting
    sort_by = request.GET.get('sort', 'default')
    if sort_by == 'newest':
        tours = tours.order_by('-created_at')
    elif sort_by == 'price_low':
        tours = tours.annotate(min_price=Min('pricing__price')).order_by('min_price')
    elif sort_by == 'price_high':
        tours = tours.annotate(min_price=Min('pricing__price')).order_by('-min_price')
    else:
        tours = tours.order_by('-is_featured', '-created_at')

    # Pagination: 12 per page
    paginator = Paginator(tours, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Taxonomy for sidebar filter options with annotated tour counts
    countries = Country.objects.filter(is_active=True).prefetch_related(
        Prefetch(
            'destinations',
            queryset=Destination.objects.filter(is_active=True).annotate(
                tour_count=Count('tours', filter=Q(tours__status='PUBLISHED'))
            ).order_by('sort_order', 'name')
        )
    ).order_by('sort_order')

    destinations = Destination.objects.filter(is_active=True).select_related('country').annotate(
        tour_count=Count('tours', filter=Q(tours__status='PUBLISHED'))
    ).order_by('sort_order')
    categories = TourCategory.objects.filter(is_active=True).order_by('sort_order')
    styles = TravelStyle.objects.all().order_by('sort_order')

    context = {
        'page_obj': page_obj,
        'tours': page_obj.object_list,
        'countries': countries,
        'destinations': destinations,
        'categories': categories,
        'styles': styles,
        'selected_country': country_slug,
        'selected_dest': dest_slug,
        'selected_category': category_slug,
        'selected_style': style_slug,
        'selected_sort': sort_by,
        'search_query': search_query,
        'total_count': paginator.count,
        'matched_country': matched_country,
        'country_destinations': country_destinations,
        'selected_dest_obj': selected_dest_obj,
    }

    if request.headers.get('HX-Request'):
        if request.headers.get('HX-Target') == 'tourResultsContainer':
            return render(request, 'tours/partials/tour_grid_partial.html', context)
        return render(request, 'tours/partials/tour_list_partial.html', context)

    return render(request, 'tours/tour-packages.html', context)


def tour_detail_view(request, slug):
    """
    Renders the comprehensive tour detail page with full itinerary, gallery, reviews, and booking box.
    """
    tour = get_object_or_404(
        Tour.objects.prefetch_related(
            'media', 'highlights', 'itinerary', 'inclusions', 
            'faqs', 'pickups', 'pricing', 'dates', 'reviews', 'surroundings', 'extra_services',
            'departures__capacities__vehicle_type', 'option_pricing__vehicle_type'
        ),
        slug=slug,
        status='PUBLISHED'
    )

    # Available departures & dates for booking widget
    available_departures = tour.departures.filter(status='OPEN').prefetch_related('capacities__vehicle_type').order_by('date', 'time')
    available_dates = tour.dates.filter(status='AVAILABLE').order_by('start_date')
    vehicle_types = VehicleType.objects.filter(is_active=True).order_by('sort_order', 'default_capacity')
    option_pricings = tour.option_pricing.filter(is_active=True).select_related('vehicle_type')

    # Base pricing
    adult_pricing = tour.pricing.filter(label__iexact='Adult').first()
    child_pricing = tour.pricing.filter(label__iexact='Child').first()
    base_price = adult_pricing.price if adult_pricing else (tour.pricing.first().price if tour.pricing.exists() else Decimal('100.00'))

    # Approved customer reviews
    reviews = tour.reviews.filter(is_approved=True).order_by('-created_at')

    # Recommended / Related tours
    related_tours = list(Tour.objects.filter(
        destination=tour.destination,
        status='PUBLISHED'
    ).exclude(id=tour.id).select_related('destination__country').prefetch_related('pricing', 'media')[:3])
    if len(related_tours) < 3:
        needed = 3 - len(related_tours)
        exclude_ids = [tour.id] + [t.id for t in related_tours]
        fallback_tours = list(Tour.objects.filter(
            status='PUBLISHED'
        ).exclude(id__in=exclude_ids).select_related('destination__country').prefetch_related('pricing', 'media')[:needed])
        related_tours.extend(fallback_tours)

    # Gallery images for popup lightbox
    gallery_images = []
    tour_media_sorted = sorted(tour.media.all(), key=lambda m: getattr(m, 'sort_order', 0))
    for m in tour_media_sorted:
        if m.file and getattr(m, 'media_type', 'IMAGE') != 'VIDEO':
            gallery_images.append({
                'url': m.file.url,
                'alt': m.alt_text or tour.title
            })
    if not gallery_images and tour.destination and tour.destination.hero_image:
        gallery_images.append({
            'url': tour.destination.hero_image.url,
            'alt': tour.title
        })
    gallery_images_json = json.dumps(gallery_images)

    context = {
        'tour': tour,
        'base_price': base_price,
        'adult_pricing': adult_pricing,
        'child_pricing': child_pricing,
        'available_departures': available_departures,
        'available_dates': available_dates,
        'vehicle_types': vehicle_types,
        'option_pricings': option_pricings,
        'reviews': reviews,
        'related_tours': related_tours,
        'gallery_images': gallery_images,
        'gallery_images_json': gallery_images_json,
    }
    return render(request, 'tours/tour-details.html', context)


def api_calculate_tour_price(request, tour_id):
    """
    JSON API endpoint for the booking widget on tour-details page.
    Computes real-time price breakdown based on departure, vehicle type, guests, and extras.
    """
    tour = get_object_or_404(Tour, id=tour_id)
    
    adults = int(request.GET.get('adults', 1))
    children = int(request.GET.get('children', 0))
    departure_id = request.GET.get('departure_id')
    vehicle_type_id = request.GET.get('vehicle_type_id') or request.GET.get('vehicle_type')
    date_id = request.GET.get('date_id')
    
    departure = None
    vehicle_type = None

    if departure_id:
        departure = Departure.objects.filter(id=departure_id, tour=tour).first()
    elif date_id:
        td = TourDate.objects.filter(id=date_id, tour=tour).first()
        if td:
            departure = Departure.objects.filter(tour=tour, date=td.start_date).first()

    if vehicle_type_id:
        vehicle_type = (
            VehicleType.objects.filter(id=vehicle_type_id).first() or
            VehicleType.objects.filter(slug=vehicle_type_id).first()
        )
    if not vehicle_type:
        vehicle_type = VehicleType.objects.filter(slug='micro').first() or VehicleType.objects.first()

    if departure and vehicle_type:
        try:
            avail_res = DepartureService.check_availability(departure, vehicle_type, adults + children)
            departure_capacity = avail_res.get('capacity') or departure.capacities.filter(vehicle_type=vehicle_type).first()
            pricing_data = DepartureService.calculate_price(
                tour=tour,
                vehicle_type=vehicle_type,
                departure_capacity=departure_capacity,
                adults=adults,
                children=children
            )
            pricing_data['is_available'] = avail_res['available']
            pricing_data['sellable_seats'] = avail_res.get('sellable', 0)
            pricing_data['availability_error'] = avail_res.get('error', '')
            return JsonResponse({'success': True, 'pricing': pricing_data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    else:
        # Legacy fallback
        tour_date = TourDate.objects.filter(id=date_id, tour=tour).first() if date_id else None
        try:
            pricing_data = TourPricingService.calculate_price(
                tour=tour,
                tour_date=tour_date,
                adults=adults,
                children=children
            )
            return JsonResponse({'success': True, 'pricing': pricing_data})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def api_submit_enquiry(request, tour_id):
    """
    JSON API endpoint for the Send Inquiry modal form.
    """
    tour = get_object_or_404(Tour, id=tour_id)
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        message = data.get('message', '').strip()

        if not name or not email or not message:
            return JsonResponse({'success': False, 'error': 'Name, email, and message are required.'}, status=400)

        enquiry = Enquiry.objects.create(
            tour=tour,
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        return JsonResponse({'success': True, 'message': 'Your inquiry has been received! Our travel team will respond within 24 hours.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def country_detail_view(request, slug):
    """
    Country Hub Page:
    Shows the country hero, all its tour places/destinations, 
    and all tour packages available in that country.
    """
    country = get_object_or_404(Country, slug=slug, is_active=True)
    destinations = country.destinations.filter(is_active=True).annotate(
        tour_count=Count('tours', filter=Q(tours__status='PUBLISHED'))
    ).order_by('sort_order')
    
    tours = Tour.objects.filter(
        destination__country=country, 
        status='PUBLISHED'
    ).prefetch_related('pricing', 'media', 'destination').order_by('-is_featured', '-created_at')

    other_countries = Country.objects.filter(is_active=True).exclude(id=country.id).order_by('sort_order')

    context = {
        'country': country,
        'destinations': destinations,
        'tours': tours,
        'other_countries': other_countries,
    }
    return render(request, 'destinations/country-details.html', context)


def destination_list_view(request):
    """Catalog of all Nordic countries and destinations."""
    countries = Country.objects.filter(is_active=True).prefetch_related('destinations').order_by('sort_order')
    destinations = Destination.objects.filter(is_active=True).select_related('country').annotate(
        tour_count=Count('tours', filter=Q(tours__status='PUBLISHED'))
    ).order_by('sort_order')
    
    country_slug = request.GET.get('country')
    if country_slug:
        destinations = destinations.filter(country__slug=country_slug)

    return render(request, 'destinations/destination.html', {
        'countries': countries,
        'destinations': destinations,
        'selected_country': country_slug,
    })


def destination_detail_view(request, slug):
    """Destination guide with overview, highlights, and all tour packages for this specific place."""
    destination = get_object_or_404(
        Destination.objects.select_related('country'), 
        slug=slug, 
        is_active=True
    )
    tours = destination.tours.filter(status='PUBLISHED').prefetch_related('pricing', 'media', 'destination')
    
    sibling_destinations = []
    if destination.country:
        sibling_destinations = destination.country.destinations.filter(
            is_active=True
        ).exclude(id=destination.id).order_by('sort_order')[:4]

    return render(request, 'destinations/destination-details.html', {
        'destination': destination, 
        'tours': tours,
        'sibling_destinations': sibling_destinations,
    })


