from .models import (
    SiteSetting, MegaMenuPromo, CompanyMenuItem,
    HomeOfferCard, PartnerLogo, ValueProposition, TeamMember,
    Testimonial, FAQItem, NavbarItem
)
from tours.models import Country, Destination, ExperienceType

def site_settings(request):
    """
    Exposes site_settings and dynamic mega menu navigation data globally to all templates.
    Whatever the admin manages in Django Admin is immediately reflected on the frontend.
    """
    settings_obj = SiteSetting.objects.first()
    if not settings_obj:
        settings_obj = SiteSetting.objects.create(
            site_name="Nord Velocity",
            tagline="Exclusive Nordic Tours & Luxury Chauffeur Services",
            hero_title="Discover the Untamed Beauty of the Nordics",
            hero_subtitle="Curated Arctic expeditions, glass igloo stays, and VIP chauffeur transfers across Finland and Scandinavia.",
            contact_email="concierge@nordvelocity.com",
            contact_phone="+358 9 1234 567",
            emergency_phone="+358 40 987 6543",
            office_address="Pohjoisesplanadi 33, 00100 Helsinki, Finland",
            operating_hours="Mon - Sun: 08:00 - 22:00 EET",
            default_currency="EUR",
            currency_symbol="€",
            facebook_url="https://facebook.com/nordvelocity",
            instagram_url="https://instagram.com/nordvelocity",
            linkedin_url="https://linkedin.com/company/nordvelocity",
            tripadvisor_url="https://tripadvisor.com",
            footer_text="Nord Velocity is Scandinavia's premier luxury travel designer, providing bespoke Arctic tours, private husky expeditions, and VIP chauffeur services.",
            copyright_text="© 2026 Nord Velocity Oy. All rights reserved."
        )

    # Dynamic Mega Menu Data
    nav_destinations = Destination.objects.filter(is_active=True, is_featured_in_nav=True).select_related('country').order_by('sort_order', 'name')[:10]
    nav_countries = Country.objects.filter(is_active=True, is_featured_in_nav=True).order_by('sort_order', 'name')[:8]
    nav_experiences = ExperienceType.objects.filter(is_featured_in_nav=True).order_by('sort_order', 'name')[:10]
    nav_company_items = CompanyMenuItem.objects.filter(is_active=True).order_by('sort_order', 'name')

    promos_qs = MegaMenuPromo.objects.filter(is_active=True)
    nav_promos = {promo.menu_type: promo for promo in promos_qs}

    # Dynamic Global Frontend Blocks
    home_offers = HomeOfferCard.objects.filter(is_active=True).order_by('sort_order', 'id')[:4]
    partner_logos = PartnerLogo.objects.filter(is_active=True).order_by('sort_order', 'id')
    value_props = ValueProposition.objects.filter(is_active=True).order_by('sort_order', 'id')[:4]
    team_members = TeamMember.objects.filter(is_active=True).order_by('sort_order', 'id')
    global_testimonials = Testimonial.objects.filter(is_featured=True).order_by('sort_order', '-created_at')[:8]
    global_faqs = FAQItem.objects.filter(is_published=True).order_by('sort_order', 'id')[:10]

    # Dynamic Navbar Links & Uploaded Icons
    navbar_items = NavbarItem.objects.filter(is_active=True).order_by('sort_order', 'id')

    # Admin Notifications System
    admin_notifications = []
    admin_unread_count = 0
    pending_bookings_count = 0
    if hasattr(request, 'user') and request.user.is_authenticated and request.user.is_staff:
        from bookings.models import Booking
        from django.utils.timesince import timesince
        from core.models import ContactSubmission

        pending_bookings_count = Booking.objects.filter(status='PENDING').count()
        bookings_qs = Booking.objects.select_related('customer').order_by('-created_at')[:4]
        for b in bookings_qs:
            t_str = timesince(b.created_at).replace('\xa0', ' ').split(',')[0] + ' ago'
            item_title = 'Direct Reservation'
            if hasattr(b, 'tour_booking') and b.tour_booking and b.tour_booking.tour:
                item_title = b.tour_booking.tour.title
            elif hasattr(b, 'chauffeur_booking') and b.chauffeur_booking and b.chauffeur_booking.vehicle:
                item_title = b.chauffeur_booking.vehicle.name
            
            cust = b.customer.email if b.customer else 'Guest'
            if b.status == 'CONFIRMED':
                admin_notifications.append({
                    'id': f'booking-{b.id}',
                    'title': 'Booking Confirmed!',
                    'message': f'Your trip ({item_title}) has been successfully confirmed. Check details in dashboard.',
                    'time_ago': t_str,
                    'url': f'/admin/bookings/booking/{b.id}/change/',
                    'icon_type': 'confirmed',
                    'is_unread': False,
                })
            elif b.status == 'PENDING':
                admin_unread_count += 1
                admin_notifications.append({
                    'id': f'booking-{b.id}',
                    'title': 'Pending Booking Approval',
                    'message': f'New reservation for {item_title} ({cust}) awaits immediate review.',
                    'time_ago': t_str,
                    'url': f'/admin/bookings/booking/{b.id}/change/',
                    'icon_type': 'pending',
                    'is_unread': True,
                })

        # Add inquiry notification if available
        for c in ContactSubmission.objects.order_by('-created_at')[:1]:
            t_str = timesince(c.created_at).replace('\xa0', ' ').split(',')[0] + ' ago'
            admin_notifications.append({
                'id': f'inquiry-{c.id}',
                'title': f'New Inquiry: {c.name}',
                'message': c.subject or 'Customer submitted an inquiry.',
                'time_ago': t_str,
                'url': f'/admin/core/contactsubmission/{c.id}/change/',
                'icon_type': 'inquiry',
                'is_unread': True,
            })
            admin_unread_count += 1

        # Add active flash sale / promo card if available
        if home_offers.exists():
            promo = home_offers.first()
            admin_notifications.append({
                'id': f'promo-{promo.id}',
                'title': promo.title or 'Flash Sale',
                'message': promo.subtitle or 'Save up to 30% on premium Nordic packages. Book before midnight!',
                'time_ago': '5 hours ago',
                'url': '/admin/core/homeoffercard/',
                'icon_type': 'flash',
                'is_unread': False,
            })

    return {
        'site_settings': settings_obj,
        'navbar_items': navbar_items,
        'nav_destinations': nav_destinations,
        'nav_countries': nav_countries,
        'nav_experiences': nav_experiences,
        'nav_company_items': nav_company_items,
        'nav_promos': nav_promos,
        'home_offers': home_offers,
        'partner_logos': partner_logos,
        'value_props': value_props,
        'team_members': team_members,
        'testimonials': global_testimonials,
        'faqs': global_faqs,
        'admin_notifications': admin_notifications,
        'admin_unread_count': admin_unread_count or pending_bookings_count,
        'pending_bookings': pending_bookings_count,
    }

