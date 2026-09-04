import os
import shutil
import django
from django.core.files import File
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from tours.models import Country, Destination, ExperienceType
from core.models import MegaMenuPromo, CompanyMenuItem

BASE_DIR = Path(__file__).resolve().parent

def attach_image(instance, field_name, source_path):
    if not source_path.exists():
        print(f"Warning: {source_path} does not exist")
        return
    with open(source_path, 'rb') as f:
        getattr(instance, field_name).save(source_path.name, File(f), save=True)

print("--- 1. Seeding Countries for Destination Sidebar ---")
countries_data = [
    ("Finland", "finland", "Northern Europe", 1),
    ("Scandinavia", "scandinavia", "Scandinavia", 2),
    ("Northern Europe", "northern-europe", "Northern Europe", 3),
    ("Western Europe", "western-europe", "Western Europe", 4),
    ("Eastern Europe", "eastern-europe", "Eastern Europe", 5),
    ("Southern Europe", "southern-europe", "Southern Europe", 6),
]

for name, slug, region, order in countries_data:
    c, _ = Country.objects.get_or_create(
        slug=slug,
        defaults={'name': name, 'region': region, 'sort_order': order, 'is_active': True, 'is_featured_in_nav': True}
    )
    c.is_featured_in_nav = True
    c.save()

finland = Country.objects.get(slug='finland')

print("--- 2. Seeding Destinations for Destination Mega Menu ---")
destinations_data = [
    ("Helsinki", "helsinki", "Frontend/images/citys/Pyha_Sunrise-550x358.jpg", 1),
    ("Rovaniemi", "rovaniemi", "Frontend/images/citys/1-Northern-Lights-Snowmobile-Levi-550x358.jpg", 2),
    ("Turku", "turku", "Frontend/images/offers/offer_1.jpg", 3),
    ("Tampere", "tampere", "Frontend/images/offers/offer_2.jpg", 4),
    ("Levi", "levi", "Frontend/images/citys/Snowmobiling-Adventure-in-Levi5-550x358.jpg", 5),
    ("Savonlinna", "savonlinna", "Frontend/images/explore/explore_1.jpg", 6),
    ("Espoo", "espoo", "Frontend/images/explore/explore_2.jpg", 7),
    ("Oulu", "oulu", "Frontend/images/explore/explore_3.jpg", 8),
    ("Porvoo", "porvoo", "Frontend/images/offers/offer_3.jpg", 9),
    ("Vaasa", "vaasa", "Frontend/images/offers/offer_4.jpg", 10),
]

for name, slug, img_rel, order in destinations_data:
    dest, created = Destination.objects.get_or_create(
        slug=slug,
        defaults={'name': name, 'country': finland, 'sort_order': order, 'is_active': True, 'is_featured_in_nav': True}
    )
    dest.is_featured_in_nav = True
    dest.sort_order = order
    dest.save()
    if not dest.hero_image:
        img_path = BASE_DIR.parent / img_rel
        if img_path.exists():
            attach_image(dest, 'hero_image', img_path)

print(f"Destinations total: {Destination.objects.count()}")

print("--- 3. Seeding Tour Categories / Experiences for Tour Mega Menu ---")
experiences_data = [
    ("Luxury", "luxury", "Frontend/images/hero/Winter-landscape-19-2-scaled.jpg", 1),
    ("Adventure", "adventure", "Frontend/images/citys/Snowmobiling-Adventure-in-Levi5-550x358.jpg", 2),
    ("Family", "family", "Frontend/images/offers/Day-Trip-to-Santa-Village7-550x358.jpg", 3),
    ("Honeymoon", "honeymoon", "Frontend/images/citys/Pyha_Sunrise-550x358.jpg", 4),
    ("Cultural", "cultural", "Frontend/images/offers/Traditional-Reindeer-Farm-Visit3-2-550x358.jpg", 5),
    ("Northern Lights", "northern-lights", "Frontend/images/citys/Northern-Lights-by-minivan6-2-550x358.jpg", 6),
    ("Icebreaker", "icebreaker", "Frontend/images/explore/explore_1.jpg", 7),
    ("Lakeland", "lakeland", "Frontend/images/explore/explore_2.jpg", 8),
    ("Winter Sports", "winter-sports", "Frontend/images/citys/1-Snowmobile-Reindeer-Husky-5-550x358.jpg", 9),
    ("City Breaks", "city-breaks", "Frontend/images/offers/offer_2.jpg", 10),
]

for name, slug, img_rel, order in experiences_data:
    exp, _ = ExperienceType.objects.get_or_create(
        slug=slug,
        defaults={'name': name, 'sort_order': order, 'is_featured_in_nav': True}
    )
    exp.is_featured_in_nav = True
    exp.sort_order = order
    exp.save()
    if not exp.image:
        img_path = BASE_DIR.parent / img_rel
        if img_path.exists():
            attach_image(exp, 'image', img_path)

print(f"Experience types total: {ExperienceType.objects.count()}")

print("--- 4. Seeding Company Menu Items ---")
company_data = [
    ("About Us", "/about/", "Frontend/images/hero/winter-aerial-nature2.jpg", 1),
    ("Our Services", "/transport/", "Frontend/images/hero/al2-scaled.jpg", 2),
    ("FAQ", "/faq/", "Frontend/images/offers/Day-Trip-to-Santa-Village7-550x358.jpg", 3),
    ("Contact", "/contact/", "Frontend/images/hero/Winter-landscape-19-2-scaled.jpg", 4),
    ("Blog", "/blog/", "Frontend/images/citys/Northern-Lights-by-minivan6-2-550x358.jpg", 5),
]

for name, url, img_rel, order in company_data:
    item, created = CompanyMenuItem.objects.get_or_create(
        name=name,
        defaults={'url': url, 'sort_order': order, 'is_active': True}
    )
    item.url = url
    item.sort_order = order
    item.is_active = True
    item.save()
    if not item.image:
        img_path = BASE_DIR.parent / img_rel
        if img_path.exists():
            attach_image(item, 'image', img_path)

print(f"Company menu items total: {CompanyMenuItem.objects.count()}")

print("--- 5. Seeding Mega Menu Promotional Banners ---")
promos = [
    {
        'menu_type': 'DESTINATION',
        'badge_text': 'up to',
        'title': '30% off SALE',
        'subtitle': '(winter offer for Lapland & Helsinki up to 30%.)',
        'description': 'Exclusive seasonal discounts on Arctic glass igloo and aurora expeditions.',
        'button_text': 'See Packages',
        'button_url': '/tours/',
        'img_rel': 'Frontend/images/hero/Winter-landscape-19-2-scaled.jpg'
    },
    {
        'menu_type': 'COMPANY',
        'badge_text': 'Exclusive',
        'title': '2026 Travel Report',
        'subtitle': 'The Future of Nordic Travel',
        'description': 'Discover the emerging trends shaping the future of global tourism and VIP luxury transport.',
        'button_text': 'Read Now',
        'button_url': '/blog/',
        'img_rel': 'Frontend/images/hero/winter-aerial-nature2.jpg'
    },
    {
        'menu_type': 'TOUR',
        'badge_text': 'Special Offer',
        'title': '15% OFF',
        'subtitle': 'Winter Packages',
        'description': 'Save 15% on curated winter aurora escapes and private husky expeditions.',
        'button_text': 'Book Now',
        'button_url': '/tours/',
        'img_rel': 'Frontend/images/citys/Self-Driving-Husky-Sledging-Tour4-550x358.jpg'
    }
]

for p in promos:
    promo, created = MegaMenuPromo.objects.get_or_create(
        menu_type=p['menu_type'],
        defaults={
            'badge_text': p['badge_text'],
            'title': p['title'],
            'subtitle': p['subtitle'],
            'description': p['description'],
            'button_text': p['button_text'],
            'button_url': p['button_url'],
            'is_active': True,
        }
    )
    promo.badge_text = p['badge_text']
    promo.title = p['title']
    promo.subtitle = p['subtitle']
    promo.description = p['description']
    promo.button_text = p['button_text']
    promo.button_url = p['button_url']
    promo.is_active = True
    promo.save()
    if not promo.background_image:
        img_path = BASE_DIR.parent / p['img_rel']
        if img_path.exists():
            attach_image(promo, 'background_image', img_path)

print("SUCCESS: Mega Menu dynamic database seeding finished cleanly!")
