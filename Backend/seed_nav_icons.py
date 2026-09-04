import os
import django
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from core.models import NavbarItem, CompanyMenuItem, SiteSetting
from tours.models import Destination, ExperienceType, Country
from django.conf import settings

# Helper to create crisp SVG icons
def make_svg_icon(svg_markup):
    return ContentFile(svg_markup.strip().encode('utf-8'))

NAV_ICONS = {
    'Home': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0066FF" width="24" height="24"><path d="M12 3L2 12h3v8h6v-6h2v6h6v-8h3L12 3z"/></svg>''',
    'Destination': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0066FF" width="24" height="24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>''',
    'Company': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0066FF" width="24" height="24"><path d="M12 7V3H2v18h20V7H12zM6 19H4v-2h2v2zm0-4H4v-2h2v2zm0-4H4V9h2v2zm0-4H4V5h2v2zm4 12H8v-2h2v2zm0-4H8v-2h2v2zm0-4H8V9h2v2zm0-4H8V5h2v2zm10 12h-8v-2h2v-2h-2v-2h2v-2h-2V9h8v10zm-2-8h-2v2h2V9zm0 4h-2v2h2v-2z"/></svg>''',
    'Tour': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0066FF" width="24" height="24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>''',
    'Transport': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0066FF" width="24" height="24"><path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.85 7h10.29l1.04 3H5.81l1.04-3zM19 17H5v-4.66l.12-.34h13.77l.11.34V17z"/><circle cx="7.5" cy="14.5" r="1.5"/><circle cx="16.5" cy="14.5" r="1.5"/></svg>''',
    'Contact': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#0066FF" width="24" height="24"><path d="M20 2H4c-1.1 0-1.99.9-1.99 2L2 22l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z"/></svg>''',
}

FLAG_ICONS = {
    'Finland': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 18 11" width="36" height="22"><rect width="18" height="11" fill="#FFFFFF"/><rect width="18" height="3" y="4" fill="#003580"/><rect width="3" height="11" x="5" fill="#003580"/></svg>''',
    'Norway': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 22 16" width="36" height="22"><rect width="22" height="16" fill="#BA0C2F"/><path d="M0 8h22M8 0v16" stroke="#FFFFFF" stroke-width="4"/><path d="M0 8h22M8 0v16" stroke="#00205B" stroke-width="2"/></svg>''',
    'Sweden': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 10" width="36" height="22"><rect width="16" height="10" fill="#006AA7"/><rect width="16" height="2" y="4" fill="#FECC00"/><rect width="2" height="10" x="5" fill="#FECC00"/></svg>''',
    'Denmark': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 37 28" width="36" height="22"><rect width="37" height="28" fill="#C60C30"/><rect width="37" height="4" y="12" fill="#FFFFFF"/><rect width="4" height="28" x="12" fill="#FFFFFF"/></svg>''',
    'Iceland': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 25 18" width="36" height="22"><rect width="25" height="18" fill="#02529C"/><path d="M0 9h25M9 0v18" stroke="#FFFFFF" stroke-width="4"/><path d="M0 9h25M9 0v18" stroke="#DC1E35" stroke-width="2"/></svg>''',
}

EXPERIENCE_ICONS = {
    'Northern Lights': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="80" height="80"><circle cx="32" cy="32" r="32" fill="#0F172A"/><path d="M16 44C24 30 40 22 48 36" stroke="#10B981" stroke-width="4" stroke-linecap="round" fill="none"/><path d="M20 50C28 36 44 28 52 42" stroke="#34D399" stroke-width="3" stroke-linecap="round" fill="none"/><circle cx="48" cy="20" r="3" fill="#FBBF24"/><circle cx="24" cy="18" r="2" fill="#FBBF24"/><circle cx="38" cy="14" r="1.5" fill="#FBBF24"/></svg>''',
    'Adventure': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="80" height="80"><circle cx="32" cy="32" r="32" fill="#1E1B4B"/><polygon points="32,16 44,46 20,46" fill="#6366F1"/><polygon points="32,22 40,46 24,46" fill="#818CF8"/><circle cx="48" cy="20" r="4" fill="#F59E0B"/></svg>''',
    'Family': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="80" height="80"><circle cx="32" cy="32" r="32" fill="#064E3B"/><circle cx="24" cy="26" r="6" fill="#34D399"/><circle cx="40" cy="26" r="6" fill="#34D399"/><circle cx="32" cy="38" r="5" fill="#A7F3D0"/><path d="M16 48c0-6 4-10 10-10h16c6 0 10 4 10 10v2H16v-2z" fill="#059669"/></svg>''',
    'Luxury': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="80" height="80"><circle cx="32" cy="32" r="32" fill="#18181B"/><polygon points="32,14 38,28 52,28 40,38 45,52 32,42 19,52 24,38 12,28 26,28" fill="#F59E0B"/></svg>''',
    'Sauna & Wellness': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="80" height="80"><circle cx="32" cy="32" r="32" fill="#7C2D12"/><path d="M24 38c0-8 6-10 6-18 0 8 6 10 6 18a6 6 0 0 1-12 0z" fill="#FB923C"/><path d="M30 46c0-6 4-7 4-13 0 6 4 7 4 13a4 4 0 0 1-8 0z" fill="#FDE047"/></svg>''',
    'default': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="80" height="80"><circle cx="32" cy="32" r="32" fill="#312E81"/><circle cx="32" cy="32" r="20" stroke="#818CF8" stroke-width="3" fill="none"/><polygon points="32,18 36,32 32,46 28,32" fill="#F43F5E"/></svg>''',
}

DESTINATION_ICONS = {
    'Rovaniemi': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="80" height="80"><circle cx="32" cy="32" r="32" fill="#0C4A6E"/><path d="M32 16l6 14h-4v8h6l-8 10-8-10h6v-8h-4z" fill="#38BDF8"/><circle cx="46" cy="18" r="3" fill="#FCD34D"/></svg>''',
    'Helsinki': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="80" height="80"><circle cx="32" cy="32" r="32" fill="#1E3A8A"/><rect x="22" y="24" width="20" height="26" fill="#93C5FD"/><polygon points="32,12 18,24 46,24" fill="#60A5FA"/><circle cx="32" cy="32" r="3" fill="#1E3A8A"/></svg>''',
    'Levi': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="80" height="80"><circle cx="32" cy="32" r="32" fill="#134E4A"/><polygon points="32,14 48,48 16,48" fill="#2DD4BF"/><polygon points="32,22 42,48 22,48" fill="#99F6E4"/></svg>''',
    'default': '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="80" height="80"><circle cx="32" cy="32" r="32" fill="#1E1B4B"/><path d="M32 16c-6.6 0-12 5.4-12 12 0 9 12 22 12 22s12-13 12-22c0-6.6-5.4-12-12-12zm0 16c-2.2 0-4-1.8-4-4s1.8-4 4-4 4 1.8 4 4-1.8 4-4 4z" fill="#A5B4FC"/></svg>'''
}

print("=== SEEDING NAVBAR ITEMS & UPLOADED NAV ICONS ===")

# 1. Navbar Items
navbar_defs = [
    ('Home', '/', 'NONE', 1),
    ('Destination', '/tours/destinations/', 'DESTINATION', 2),
    ('Company', '/about/', 'COMPANY', 3),
    ('Tour', '/tours/', 'TOUR', 4),
    ('Transport', '/transport/', 'NONE', 5),
    ('Contact', '/contact/', 'NONE', 6),
]

for title, url, menu_type, sort_order in navbar_defs:
    nav_item, created = NavbarItem.objects.get_or_create(
        title=title,
        defaults={
            'url': url,
            'menu_type': menu_type,
            'sort_order': sort_order,
            'is_active': True,
        }
    )
    if not nav_item.icon:
        svg_content = NAV_ICONS.get(title, NAV_ICONS['Home'])
        nav_item.icon.save(f"nav_{title.lower()}.svg", make_svg_icon(svg_content), save=True)
        print(f"Created uploaded icon for NavbarItem: {title}")
    else:
        print(f"NavbarItem: {title} already has icon: {nav_item.icon.name}")

# 2. Country Flag Icons
for country in Country.objects.all():
    flag_svg = FLAG_ICONS.get(country.name)
    if flag_svg and not country.flag_icon:
        country.flag_icon.save(f"flag_{country.slug}.svg", make_svg_icon(flag_svg), save=True)
        print(f"Uploaded flag icon for country: {country.name}")

# 3. Destination Nav Icons
for dest in Destination.objects.all():
    if not dest.nav_icon:
        # Check if we have hero_image or custom SVG
        if dest.hero_image:
            # Copy hero_image reference to nav_icon
            dest.nav_icon.name = dest.hero_image.name
            dest.save()
            print(f"Bound nav_icon for destination from hero_image: {dest.name}")
        else:
            dest_svg = DESTINATION_ICONS.get(dest.name, DESTINATION_ICONS['default'])
            dest.nav_icon.save(f"nav_dest_{dest.slug}.svg", make_svg_icon(dest_svg), save=True)
            print(f"Uploaded custom nav_icon for destination: {dest.name}")

# 4. Experience Type Nav Icons
for exp in ExperienceType.objects.all():
    if not exp.nav_icon:
        if exp.image:
            exp.nav_icon.name = exp.image.name
            exp.save()
            print(f"Bound nav_icon for experience from image: {exp.name}")
        else:
            exp_svg = EXPERIENCE_ICONS.get(exp.name, EXPERIENCE_ICONS['default'])
            exp.nav_icon.save(f"nav_exp_{exp.slug}.svg", make_svg_icon(exp_svg), save=True)
            print(f"Uploaded custom nav_icon for experience: {exp.name}")

# 5. Company Menu Items - ensure all have valid images
for item in CompanyMenuItem.objects.all():
    if not item.image:
        item_svg = NAV_ICONS.get('Company')
        item.image.save(f"company_{item.id}.svg", make_svg_icon(item_svg), save=True)
        print(f"Uploaded icon for company menu item: {item.name}")

print("Nav icon seeding completed successfully!")
