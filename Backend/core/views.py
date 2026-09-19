import json
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
from django.db.models import Prefetch, Count, Q
from tours.models import Country, Tour, Destination, TourCategory
from content.models import BlogPost
from .models import ContactSubmission, FAQItem, Testimonial, SiteSetting


def get_bento_catalog(countries, destinations):
    """
    Constructs dynamic Bento destination catalog grouped by region/category strictly from database models.
    Returns a dict with region slugs as keys and list of pages (each page up to 5 items) as values.
    """
    colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#06B6D4']
    region_keys = [
        'popular',
        'north-islands',
        'northern-europe',
        'western-europe',
        'eastern-europe',
        'southern-europe'
    ]
    items_by_region = {r: [] for r in region_keys}

    region_map = {
        'finland': 'northern-europe',
        'norway': 'northern-europe',
        'sweden': 'northern-europe',
        'denmark': 'northern-europe',
        'iceland': 'north-islands',
        'greenland': 'north-islands',
        'svalbard': 'north-islands',
        'faroe-islands': 'north-islands',
    }

    # Add Countries
    for c in countries:
        try:
            c_url = reverse('tours:country_detail', args=[c.slug])
        except Exception:
            c_url = f"/tours/?country={c.slug}"
        img = c.hero_image.url if c.hero_image else '/static/images/hero/Winter-landscape-19-2-scaled.jpg'
        reg = (c.region or '').strip().lower().replace(' ', '-')
        if not reg or reg not in items_by_region:
            reg = region_map.get(c.slug, 'popular')

        desc = c.subtitle or c.description or f"Explore breathtaking tours and experiences in {c.name}."
        if len(desc) > 100:
            desc = desc[:97] + '...'

        item = {
            'name': c.name,
            'url': c_url,
            'image': img,
            'desc': desc,
        }
        if reg in items_by_region:
            items_by_region[reg].append(item)
        items_by_region['popular'].append(item)

    # Add Destinations
    for d in destinations:
        d_url = f"/tours/?destination={d.slug}"
        img = d.hero_image.url if d.hero_image else (d.nav_icon.url if d.nav_icon else '/static/images/hero/Winter-landscape-19-2-scaled.jpg')
        reg = 'popular'
        if d.country:
            c_reg = (d.country.region or '').strip().lower().replace(' ', '-')
            reg = c_reg if c_reg in items_by_region else region_map.get(d.country.slug, 'popular')

        desc = d.highlights or d.description or f"Discover unforgettable adventures and stays in {d.name}."
        if len(desc) > 100:
            desc = desc[:97] + '...'

        item = {
            'name': d.name,
            'url': d_url,
            'image': img,
            'desc': desc,
        }
        if reg in items_by_region and reg != 'popular':
            items_by_region[reg].append(item)
        if len(items_by_region['popular']) < 15:
            items_by_region['popular'].append(item)

    # Chunk into pages of 5 items
    catalog = {}
    for reg, items in items_by_region.items():
        if not items:
            catalog[reg] = []
            continue
        pages = []
        for i in range(0, len(items), 5):
            chunk = items[i:i+5]
            page_items = []
            for idx, raw in enumerate(chunk):
                page_items.append({
                    'tall': (idx == 0),
                    'name': raw['name'],
                    'badgeDot': colors[idx % len(colors)],
                    'url': raw['url'],
                    'image': raw['image'],
                    'desc': raw['desc'],
                })
            pages.append(page_items)
        catalog[reg] = pages

    return catalog


def home_view(request):
    """
    Renders the homepage with dynamic tours, countries, popular destinations, categories, testimonials, and blog stories.
    All data is completely dynamic and editable from the Django Admin Panel!
    """
    featured_tours = Tour.objects.filter(
        status='PUBLISHED'
    ).prefetch_related('pricing', 'media', 'destination', 'travel_style').order_by('-is_featured', '-created_at')

    active_dest_qs = Destination.objects.filter(is_active=True).annotate(
        tour_count=Count('tours', filter=Q(tours__status='PUBLISHED'))
    ).order_by('sort_order', 'name')

    countries = Country.objects.filter(is_active=True).prefetch_related(
        Prefetch('destinations', queryset=active_dest_qs)
    ).order_by('sort_order')
    finland = countries.filter(slug='finland').first()
    other_countries = countries.exclude(slug='finland').exclude(hero_image__exact='').exclude(hero_image__isnull=True)[:4]
    if not other_countries.exists():
        other_countries = countries.exclude(slug='finland')[:4]

    destinations = Destination.objects.filter(is_active=True).annotate(
        tour_count=Count('tours', filter=Q(tours__status='PUBLISHED'))
    ).order_by('sort_order')[:8]
    categories = TourCategory.objects.filter(is_active=True).order_by('sort_order')[:6]
    testimonials = Testimonial.objects.filter(is_featured=True).order_by('sort_order')[:4]
    recent_posts = BlogPost.objects.filter(status='PUBLISHED').order_by('-publish_date', '-created_at')[:3]

    bento_catalog = get_bento_catalog(countries, destinations)
    bento_catalog_json = json.dumps(bento_catalog)

    context = {
        'featured_tours': featured_tours,
        'countries': countries,
        'finland': finland,
        'other_countries': other_countries,
        'destinations': destinations,
        'categories': categories,
        'testimonials': testimonials,
        'recent_posts': recent_posts,
        'bento_catalog_json': bento_catalog_json,
    }
    return render(request, 'core/index.html', context)


def about_view(request):
    """Renders the About Us page with dynamic stats and testimonials."""
    testimonials = Testimonial.objects.filter(is_featured=True).order_by('sort_order')[:3]
    return render(request, 'core/about.html', {'testimonials': testimonials})


def faq_view(request):
    """Renders the Frequently Asked Questions page with dynamic questions from the admin panel."""
    faqs = FAQItem.objects.filter(is_published=True).order_by('sort_order')
    return render(request, 'core/faq.html', {'faqs': faqs})


def contact_view(request):
    """
    Renders the Contact Us page and handles form submissions.
    Contact information and map are pulled directly from SiteSetting.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', 'General Inquiry').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            ContactSubmission.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            messages.success(request, "Thank you! Your message has been sent. We'll be in touch soon.")
        else:
            messages.error(request, "Please fill in all required fields (Name, Email, Message).")

    return render(request, 'core/contact.html')
