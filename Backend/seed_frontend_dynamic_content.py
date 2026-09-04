import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.core.files import File
from core.models import (
    SiteSetting, HomeOfferCard, PartnerLogo, TeamMember, 
    ValueProposition, FAQItem, Testimonial
)

def seed_all():
    print("=== SEEDING FRONTEND DYNAMIC DATA ===")

    # 1. Update SiteSetting with rich stats, mission, and app metrics
    setting = SiteSetting.objects.first()
    if setting:
        setting.stat_tours_completed = "26K+"
        setting.stat_years_experience = "15+"
        setting.stat_happy_travelers = "15,000+"
        setting.stat_satisfaction_rate = "98%"
        setting.stat_rating_display = "4.9"
        setting.mission_title = "We're Top Travel Agency in the Nordics."
        setting.mission_description = "Discover the magic of the Arctic with the experts. We offer unparalleled experiences across the breathtaking landscapes of Finland and Scandinavia."
        setting.mission_statement = "To provide authentic, unforgettable Nordic adventures while promoting sustainable tourism and respecting local traditions."
        vision_statement = "To be the global benchmark for Arctic travel, ensuring every guest leaves with a deep appreciation for the North."
        setting.founder_name = "Nord Velocity Founders"
        setting.founder_title = "Executive Management"
        setting.app_store_url = "https://apple.com/app-store"
        setting.play_store_url = "https://play.google.com"
        setting.app_rating = "4.9"
        setting.app_reviews_count = "12,300+"
        setting.app_active_users = "2M+"
        setting.save()
        print("Updated SiteSetting with stats, mission statements, and app store configurations.")

    # 2. Seed HomeOfferCards (4 items)
    offers_data = [
        {
            'title': 'NORDIC WINTER WONDERLAND',
            'subtitle': 'Lapland Snowmobile & Husky Safari',
            'badge_text': '25% off',
            'price_badge': '$199/only',
            'url': '/tours/',
            'sort_order': 1,
            'source_img': '../Frontend/images/offers/Day-Trip-to-Santa-Village7-550x358.jpg',
            'target_name': 'offer_nordic_winter.jpg',
        },
        {
            'title': 'ARCTIC ADVENTURE AWAITS',
            'subtitle': 'Snow Village Expeditions',
            'badge_text': 'Special',
            'price_badge': '$249/only',
            'url': '/tours/',
            'sort_order': 2,
            'source_img': '../Frontend/images/offers/Snow-Village-by-Snowmobile4-550x358.jpg',
            'target_name': 'offer_snow_village.jpg',
        },
        {
            'title': 'NORTHERN LIGHTS SALE',
            'subtitle': 'Aurora Glass Igloo Stays',
            'badge_text': 'up to 20% off',
            'price_badge': 'SALE',
            'url': '/tours/',
            'sort_order': 3,
            'source_img': '../Frontend/images/offers/Northern-Lights-By-Snowmobile-5-550x358.jpg',
            'target_name': 'offer_northern_lights.jpg',
        },
        {
            'title': 'MIDNIGHT SUN & REINDEER',
            'subtitle': 'Traditional Reindeer Farm Visit',
            'badge_text': 'Summer Mode',
            'price_badge': '$199 only',
            'url': '/tours/',
            'sort_order': 4,
            'source_img': '../Frontend/images/offers/Traditional-Reindeer-Farm-Visit3-2-550x358.jpg',
            'target_name': 'offer_reindeer_farm.jpg',
        },
    ]

    for data in offers_data:
        offer, created = HomeOfferCard.objects.get_or_create(
            title=data['title'],
            defaults={
                'subtitle': data['subtitle'],
                'badge_text': data['badge_text'],
                'price_badge': data['price_badge'],
                'url': data['url'],
                'sort_order': data['sort_order'],
                'is_active': True,
            }
        )
        if os.path.exists(data['source_img']) and not offer.image:
            with open(data['source_img'], 'rb') as f:
                offer.image.save(data['target_name'], File(f), save=True)
        print(f"Offer Card: {offer.title} (Created: {created})")

    # 3. Seed PartnerLogos (6 marquee partners)
    partners_data = [
        {'name': 'Visit Finland', 'url': 'https://www.visitfinland.com', 'sort_order': 1},
        {'name': 'Lapland Safaris', 'url': 'https://www.laplandsafaris.com', 'sort_order': 2},
        {'name': 'Finnair Airlines', 'url': 'https://www.finnair.com', 'sort_order': 3},
        {'name': 'Scandic Hotels', 'url': 'https://www.scandichotels.com', 'sort_order': 4},
        {'name': 'Nordic Luxury Group', 'url': '#', 'sort_order': 5},
        {'name': 'Arctic Circle Wilderness', 'url': '#', 'sort_order': 6},
    ]
    for p_data in partners_data:
        partner, created = PartnerLogo.objects.get_or_create(
            name=p_data['name'],
            defaults={'url': p_data['url'], 'sort_order': p_data['sort_order'], 'is_active': True}
        )
        print(f"Partner Logo: {partner.name} (Created: {created})")

    # 4. Seed Leadership Team Members (4 members)
    team_data = [
        {
            'name': 'Mikael Lindholm',
            'role': 'Chief Executive Officer',
            'bio': 'Over 18 years leading luxury Scandinavian travel operations and Arctic safari expeditions.',
            'linkedin_url': 'https://linkedin.com',
            'sort_order': 1,
            'source_img': '../Frontend/images/team/travelers-img1.png',
            'target_name': 'mikael_lindholm.png',
        },
        {
            'name': 'Aleksi Koskinen',
            'role': 'Head of Arctic Operations',
            'bio': 'Native Lapland expedition leader overseeing private snowmobile, husky, and aurora hunting routes.',
            'linkedin_url': 'https://linkedin.com',
            'sort_order': 2,
            'source_img': '../Frontend/images/team/testimonial-author-img4.png',
            'target_name': 'aleksi_koskinen.png',
        },
        {
            'name': 'Sofia Rantanen',
            'role': 'VIP Concierge & Client Director',
            'bio': 'Specialist in tailor-made luxury itineraries and 24/7 high-profile private client care.',
            'linkedin_url': 'https://linkedin.com',
            'sort_order': 3,
            'source_img': '../Frontend/images/team/travelers-img2.png',
            'target_name': 'sofia_rantanen.png',
        },
        {
            'name': 'Jari Korhonen',
            'role': 'Fleet & VIP Chauffeur Manager',
            'bio': 'Managing executive armored and luxury Mercedes-Benz chauffeur transfers across Helsinki and Lapland.',
            'linkedin_url': 'https://linkedin.com',
            'sort_order': 4,
            'source_img': '../Frontend/images/team/travelers-img1.png',
            'target_name': 'jari_korhonen.png',
        },
    ]
    for t_data in team_data:
        member, created = TeamMember.objects.get_or_create(
            name=t_data['name'],
            defaults={
                'role': t_data['role'],
                'bio': t_data['bio'],
                'linkedin_url': t_data['linkedin_url'],
                'sort_order': t_data['sort_order'],
                'is_active': True,
            }
        )
        if os.path.exists(t_data['source_img']) and not member.photo:
            with open(t_data['source_img'], 'rb') as f:
                member.photo.save(t_data['target_name'], File(f), save=True)
        print(f"Team Member: {member.name} ({member.role}) (Created: {created})")

    # 5. Seed ValuePropositions (4 features)
    value_data = [
        {
            'title': 'Best Price Guarantee Ever.',
            'description': "Travel confidently knowing you're getting the best value - competitive prices with no hidden costs.",
            'icon_class': 'ph-bold ph-star',
            'bg_color_class': 'bg-light-green',
            'sort_order': 1,
        },
        {
            'title': 'Safe, Secure & Hassle-Free Booking.',
            'description': 'Plan and confirm your trip quickly with our safe, simple, and fully secure booking system.',
            'icon_class': 'ph-bold ph-shield-check',
            'bg_color_class': 'bg-light-gray',
            'sort_order': 2,
        },
        {
            'title': 'Flexible & Custom Travel Packages.',
            'description': 'Plan your trip your way with flexible travel packages tailored to your schedule and custom desires.',
            'icon_class': 'ph-bold ph-train',
            'bg_color_class': 'bg-light-teal',
            'sort_order': 3,
        },
        {
            'title': 'Our Support Always with You 24/7.',
            'description': 'Travel with complete peace of mind knowing our expert concierge team is always ready to support you.',
            'icon_class': 'ph-bold ph-chats-circle',
            'bg_color_class': 'bg-light-purple',
            'sort_order': 4,
        },
    ]
    for v_data in value_data:
        vp, created = ValueProposition.objects.get_or_create(
            title=v_data['title'],
            defaults={
                'description': v_data['description'],
                'icon_class': v_data['icon_class'],
                'bg_color_class': v_data['bg_color_class'],
                'sort_order': v_data['sort_order'],
                'is_active': True,
            }
        )
        print(f"Value Proposition: {vp.title} (Created: {created})")

    print("\nSUCCESS: All frontend dynamic content successfully seeded!")

if __name__ == '__main__':
    seed_all()
