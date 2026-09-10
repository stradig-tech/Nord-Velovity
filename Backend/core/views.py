from django.shortcuts import render
from django.contrib import messages
from tours.models import Country, Tour, Destination, TourCategory
from content.models import BlogPost
from .models import ContactSubmission, FAQItem, Testimonial, SiteSetting

def home_view(request):
    """
    Renders the homepage with dynamic tours, countries, popular destinations, categories, testimonials, and blog stories.
    All data is completely dynamic and editable from the Django Admin Panel!
    """
    featured_tours = Tour.objects.filter(
        status='PUBLISHED'
    ).prefetch_related('pricing', 'media', 'destination', 'travel_style').order_by('-is_featured', '-created_at')

    countries = Country.objects.filter(is_active=True).prefetch_related('destinations').order_by('sort_order')
    finland = countries.filter(slug='finland').first()
    other_countries = countries.exclude(slug='finland').exclude(hero_image__exact='').exclude(hero_image__isnull=True)[:4]
    if not other_countries.exists():
        other_countries = countries.exclude(slug='finland')[:4]

    destinations = Destination.objects.filter(is_active=True).order_by('sort_order')[:8]
    categories = TourCategory.objects.filter(is_active=True).order_by('sort_order')[:6]
    testimonials = Testimonial.objects.filter(is_featured=True).order_by('sort_order')[:4]
    recent_posts = BlogPost.objects.filter(status='PUBLISHED').order_by('-publish_date', '-created_at')[:3]

    context = {
        'featured_tours': featured_tours,
        'countries': countries,
        'finland': finland,
        'other_countries': other_countries,
        'destinations': destinations,
        'categories': categories,
        'testimonials': testimonials,
        'recent_posts': recent_posts,
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
