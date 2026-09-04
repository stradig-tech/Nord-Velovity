import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Min, Count

from .models import (
    Country, Tour, Destination, Season, ExperienceType, TravelStyle, 
    TourCategory, TourDate, TourPricing
)
from .services import TourPricingService
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
    if country_slug:
        tours = tours.filter(destination__country__slug=country_slug)

    # Destination filter
    dest_slug = request.GET.get('destination')
    if dest_slug:
        tours = tours.filter(destination__slug=dest_slug)

    # Category / Experience filter
    category_slug = request.GET.get('category')
    if category_slug:
        tours = tours.filter(experience_types__slug=category_slug)

    # Travel Style filter
    style_slug = request.GET.get('style')
    if style_slug:
        tours = tours.filter(travel_style__slug=style_slug)

    # Search Query
    search_query = request.GET.get('q')
    if search_query:
        tours = tours.filter(
            Q(title__icontains=search_query) |
            Q(short_summary__icontains=search_query) |
            Q(overview__icontains=search_query) |
            Q(destination__name__icontains=search_query)
        )

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

    # Taxonomy for sidebar filter options
    countries = Country.objects.filter(is_active=True).prefetch_related('destinations').order_by('sort_order')
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
    }
    return render(request, 'tour-packages.html', context)


def tour_detail_view(request, slug):
    """
    Renders the comprehensive tour detail page with full itinerary, gallery, reviews, and booking box.
    """
    tour = get_object_or_404(
        Tour.objects.prefetch_related(
            'media', 'highlights', 'itinerary', 'inclusions', 
            'faqs', 'pickups', 'pricing', 'dates', 'reviews', 'surroundings', 'extra_services'
        ),
        slug=slug,
        status='PUBLISHED'
    )

    # Available dates for booking widget
    available_dates = tour.dates.filter(status='AVAILABLE').order_by('start_date')

    # Base pricing
    adult_pricing = tour.pricing.filter(label__iexact='Adult').first()
    child_pricing = tour.pricing.filter(label__iexact='Child').first()
    base_price = adult_pricing.price if adult_pricing else (tour.pricing.first().price if tour.pricing.exists() else Decimal('100.00'))

    # Approved customer reviews
    reviews = tour.reviews.filter(is_approved=True).order_by('-created_at')

    # Recommended / Related tours
    related_tours = Tour.objects.filter(
        destination=tour.destination,
        status='PUBLISHED'
    ).exclude(id=tour.id).prefetch_related('pricing')[:3]

    context = {
        'tour': tour,
        'base_price': base_price,
        'adult_pricing': adult_pricing,
        'child_pricing': child_pricing,
        'available_dates': available_dates,
        'reviews': reviews,
        'related_tours': related_tours,
    }
    return render(request, 'tour-details.html', context)


def api_calculate_tour_price(request, tour_id):
    """
    JSON API endpoint for the Vue.js booking widget on tour-details page.
    Computes real-time price breakdown based on selected guests, dates, and extras.
    """
    tour = get_object_or_404(Tour, id=tour_id)
    
    adults = int(request.GET.get('adults', 1))
    children = int(request.GET.get('children', 0))
    date_id = request.GET.get('date_id')
    
    tour_date = None
    if date_id:
        tour_date = TourDate.objects.filter(id=date_id, tour=tour).first()

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
    return render(request, 'country-details.html', context)


def destination_list_view(request):
    """Catalog of all Nordic countries and destinations."""
    countries = Country.objects.filter(is_active=True).prefetch_related('destinations').order_by('sort_order')
    destinations = Destination.objects.filter(is_active=True).select_related('country').annotate(
        tour_count=Count('tours', filter=Q(tours__status='PUBLISHED'))
    ).order_by('sort_order')
    
    country_slug = request.GET.get('country')
    if country_slug:
        destinations = destinations.filter(country__slug=country_slug)

    return render(request, 'destination.html', {
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

    return render(request, 'destination-details.html', {
        'destination': destination, 
        'tours': tours,
        'sibling_destinations': sibling_destinations,
    })


