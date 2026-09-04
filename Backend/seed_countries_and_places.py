import os, shutil, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.conf import settings
from tours.models import (
    Country, Destination, Tour, TravelStyle, DurationBand, 
    TourPricing, TourMedia
)

frontend_images = os.path.abspath('../Frontend/images')
countries_media_dir = os.path.join(settings.MEDIA_ROOT, 'countries')
dest_media_dir = os.path.join(settings.MEDIA_ROOT, 'destinations')
os.makedirs(countries_media_dir, exist_ok=True)
os.makedirs(dest_media_dir, exist_ok=True)

# 1. Countries
country_data = [
    {
        'name': 'Finland',
        'slug': 'finland',
        'region': 'Popular',
        'subtitle': 'Land of a thousand lakes, midnight sun, and magical northern lights.',
        'description': 'Finland is a world of pristine wilderness, clean air, and magical winter adventures. From the vibrant cultural design capital of Helsinki to the snowy fells of Lapland with Santa Claus and dancing Aurora Borealis, Finland offers an unforgettable escape.',
        'src_img': os.path.join(frontend_images, 'citys', '15-Kilometers-Self-Driving-Husky-Tour-in-Levi1-2-550x358.jpg'),
        'sort_order': 1
    },
    {
        'name': 'Norway',
        'slug': 'norway',
        'region': 'Popular',
        'subtitle': 'Dramatic fjords, majestic mountains, and arctic coastal expeditions.',
        'description': 'Norway captivates with dramatic deep fjords, towering peaks, and vibrant coastal cities. Experience the midnight sun, whale safaris, scenic railways, and world-renowned arctic landscapes.',
        'src_img': os.path.join(frontend_images, 'citys', 'Northern-Lights-by-minivan6-2-550x358.jpg'),
        'sort_order': 2
    },
    {
        'name': 'Sweden',
        'slug': 'sweden',
        'region': 'Popular',
        'subtitle': 'Sophisticated Nordic design, vast royal forests, and arctic wonder.',
        'description': 'From the cobblestone streets of Stockholm to the ice hotels and vast wilderness of Swedish Lapland, Sweden blends rich history with modern luxury and untouched natural beauty.',
        'src_img': os.path.join(frontend_images, 'citys', 'Pyha_Sunrise-550x358.jpg'),
        'sort_order': 3
    },
    {
        'name': 'Denmark',
        'slug': 'denmark',
        'region': 'Popular',
        'subtitle': 'Fairy-tale royal castles, coastal dunes, and cozy hygge culture.',
        'description': 'Denmark charms visitors with historic castles, coastal serenity, and Copenhagen\'s world-renowned culinary and architectural scene.',
        'src_img': os.path.join(frontend_images, 'citys', '1-Snowmobile-Reindeer-Husky-5-550x358.jpg'),
        'sort_order': 4
    },
    {
        'name': 'Iceland',
        'slug': 'iceland',
        'region': 'Popular',
        'subtitle': 'Geothermal blue lagoons, thunderous waterfalls, and volcanic glaciers.',
        'description': 'Iceland is the land of fire and ice, featuring dramatic volcanoes, steaming geothermal spas, ice caves, and thunderous waterfalls.',
        'src_img': os.path.join(frontend_images, 'citys', 'Snowmobiling-Adventure-in-Levi5-550x358.jpg'),
        'sort_order': 5
    },
]

countries_map = {}
for c in country_data:
    country, _ = Country.objects.get_or_create(slug=c['slug'], defaults={'name': c['name']})
    country.name = c['name']
    country.region = c['region']
    country.subtitle = c['subtitle']
    country.description = c['description']
    country.sort_order = c['sort_order']
    country.is_active = True
    
    if os.path.exists(c['src_img']):
        fname = f"{c['slug']}_{os.path.basename(c['src_img'])}"
        dest_file = os.path.join(countries_media_dir, fname)
        shutil.copy2(c['src_img'], dest_file)
        country.hero_image = f"countries/{fname}"
    country.save()
    countries_map[c['slug']] = country
    print(f"[OK] Country saved: {country.name}")

# Remove unnecessary country if present
Country.objects.filter(slug='bangladesh').delete()

# 2. Destinations / Tour Places
destination_data = [
    # Finland Places
    {
        'country': 'finland',
        'name': 'Helsinki',
        'slug': 'helsinki',
        'description': 'Finland\'s stylish coastal capital, celebrated for neoclassical and modern architecture, vibrant food halls, and the sea fortress of Suomenlinna.',
        'highlights': 'Suomenlinna Fortress, Helsinki Cathedral, Design District, Market Square, Löyly Public Sauna',
        'src_img': os.path.join(frontend_images, 'packages', '65535_54274700516_8d0245d0c1_b_800_600_nofilter.jpg'),
        'sort_order': 1
    },
    {
        'country': 'finland',
        'name': 'Rovaniemi',
        'slug': 'rovaniemi',
        'description': 'The Official Hometown of Santa Claus on the Arctic Circle. A dream winter wonderland with glass igloos, reindeer safaris, and dancing Aurora Borealis.',
        'highlights': 'Santa Claus Village, Arctic Circle Line, Thermal Glass Igloos, Arktikum Science Center, Reindeer Sleighs',
        'src_img': os.path.join(frontend_images, 'packages', '31337_54406107252_f4ca19b35f_c_800_600_nofilter.jpg'),
        'sort_order': 2
    },
    {
        'country': 'finland',
        'name': 'Levi',
        'slug': 'levi',
        'description': 'Finland\'s premier ski resort and outdoor adventure capital in western Lapland, boasting world-class snowmobiling trails, husky sledding, and ice hotels.',
        'highlights': 'Levi Ski Resort, Husky Safari Trails, Snowmobile Wilderness Expeditions, Snow Village Ice Hotel',
        'src_img': os.path.join(frontend_images, 'citys', '15-Kilometers-Self-Driving-Husky-Tour-in-Levi1-2-550x358.jpg'),
        'sort_order': 3
    },
    {
        'country': 'finland',
        'name': 'Finnish Lakeland',
        'slug': 'lakeland',
        'description': 'Europe\'s largest lake labyrinth, offering peaceful pine forests, private log villa retreats, authentic wood-burning saunas, and crystal-clear freshwater.',
        'highlights': 'Private Lake Saunas, Log Villa Lodges, Lake Saimaa Cruises, Saimaa Ringed Seal Spotting',
        'src_img': os.path.join(frontend_images, 'packages', '7111_13901216855_cca37b8607_b_800_600_nofilter.jpg'),
        'sort_order': 4
    },
    {
        'country': 'finland',
        'name': 'Inari & Saariselkä',
        'slug': 'inari-saariselka',
        'description': 'Wild northern Lapland and the spiritual heart of the indigenous Sámi culture, renowned for pristine fell landscapes, gold panning, and dark sky aurora viewing.',
        'highlights': 'Siida Sámi Museum, Lake Inari Wilderness, Urho Kekkonen National Park, Aurora Fells',
        'src_img': os.path.join(frontend_images, 'citys', '1-Northern-Lights-Snowmobile-Levi-550x358.jpg'),
        'sort_order': 5
    },
    {
        'country': 'finland',
        'name': 'Turku & Archipelago',
        'slug': 'turku-archipelago',
        'description': 'Finland\'s oldest city and cultural capital, surrounded by over 20,000 islands forming the largest archipelago sea in the world.',
        'highlights': 'Turku Medieval Castle, Archipelago Trail, Aura River Walk, Maritime Forum Marinum',
        'src_img': os.path.join(frontend_images, 'packages', '65535_54407223633_9fc6ebf472_c_800_600_nofilter.jpg'),
        'sort_order': 6
    },
    # Norway Places
    {
        'country': 'norway',
        'name': 'Tromsø',
        'slug': 'tromso',
        'description': 'The Capital of the Arctic and Norway\'s ultimate base for northern lights chasing, whale watching in winter fjords, and arctic wildlife.',
        'highlights': 'Arctic Cathedral, Fjellheisen Cable Car, Fjord Whale Watching, Northern Lights Chase',
        'src_img': os.path.join(frontend_images, 'citys', 'Northern-Lights-by-minivan6-2-550x358.jpg'),
        'sort_order': 1
    },
    {
        'country': 'norway',
        'name': 'Oslo',
        'slug': 'oslo',
        'description': 'Norway\'s fast-evolving capital combining modern waterfront architecture, Munch art museum, and scenic fjord cruises.',
        'highlights': 'Oslo Opera House, Vigeland Sculpture Park, Munch Museum, Akershus Fortress',
        'src_img': os.path.join(frontend_images, 'citys', 'Snowmobiling-Adventure-in-Levi5-550x358.jpg'),
        'sort_order': 2
    },
    # Sweden Places
    {
        'country': 'sweden',
        'name': 'Stockholm',
        'slug': 'stockholm',
        'description': 'The Venice of the North spread across 14 islands, featuring historic Gamla Stan, the Royal Palace, and modern Nordic gourmet cuisine.',
        'highlights': 'Gamla Stan Medieval Town, Vasa Maritime Museum, Royal Palace, Stockholm Archipelago Cruise',
        'src_img': os.path.join(frontend_images, 'citys', 'Pyha_Sunrise-550x358.jpg'),
        'sort_order': 1
    },
    {
        'country': 'sweden',
        'name': 'Kiruna & Abisko',
        'slug': 'kiruna-abisko',
        'description': 'Swedish Lapland\'s iconic northern outpost, home of the world-famous Icehotel and the cloud-free Abisko Aurora Sky Station.',
        'highlights': 'Original Icehotel, Abisko National Park, Aurora Sky Station, Kebnekaise Mountain',
        'src_img': os.path.join(frontend_images, 'packages', '31337_54406107252_f4ca19b35f_c_800_600_nofilter.jpg'),
        'sort_order': 2
    },
    # Denmark Places
    {
        'country': 'denmark',
        'name': 'Copenhagen',
        'slug': 'copenhagen',
        'description': 'Denmark\'s vibrant capital of design, canals, Tivoli Gardens, and historic royal palaces.',
        'highlights': 'Nyhavn Harbor, Tivoli Gardens, Amalienborg Royal Palace, The Little Mermaid',
        'src_img': os.path.join(frontend_images, 'citys', '1-Snowmobile-Reindeer-Husky-5-550x358.jpg'),
        'sort_order': 1
    },
]

# Clean up broken typo destinations if any
Destination.objects.filter(slug='the-little-mermeid').delete()

dest_map = {}
for d in destination_data:
    country = countries_map.get(d['country'])
    dest, _ = Destination.objects.get_or_create(slug=d['slug'], defaults={'name': d['name']})
    dest.name = d['name']
    dest.country = country
    dest.description = d['description']
    dest.highlights = d['highlights']
    dest.sort_order = d['sort_order']
    dest.is_active = True
    
    if os.path.exists(d['src_img']):
        fname = f"{d['slug']}_{os.path.basename(d['src_img'])}"
        dest_file = os.path.join(dest_media_dir, fname)
        shutil.copy2(d['src_img'], dest_file)
        dest.hero_image = f"destinations/{fname}"
        dest.hero_image_alt = f"{dest.name} Landscape"
    dest.save()
    dest_map[d['slug']] = dest
    print(f"[OK] Destination saved: {dest.name} ({country.name})")

# Ensure existing tours link to valid destinations
t_lakeland = Tour.objects.filter(slug='finnish-lakeland-luxury-sauna-villa-retreat').first()
if t_lakeland and 'lakeland' in dest_map:
    t_lakeland.destination = dest_map['lakeland']
    t_lakeland.save()

# Let's also create 1 sample tour for Norway and 1 for Sweden so every country has packages!
style = TravelStyle.objects.first()
band = DurationBand.objects.first()

# Norway Tour: Tromso Northern Lights & Fjord Cruise
norway_tour, created = Tour.objects.get_or_create(
    slug='norway-tromso-northern-lights-fjord-expedition',
    defaults={
        'title': 'Tromsø Northern Lights & Fjord Whale Expedition',
        'short_summary': 'Witness the arctic wonders of northern Norway with silent fjord catamaran cruises and wilderness aurora hunts.',
        'overview': 'Embark on an unforgettable journey in Tromsø, the Paris of the North. Sail through snow-dusted fjords searching for humpback whales, visit husky camps, and chase the northern lights in dark sky locations.',
        'destination': dest_map.get('tromso', dest_map.get('oslo')),
        'travel_style': style,
        'duration_band': band,
        'duration_text': '5 Days / 4 Nights',
        'status': 'PUBLISHED',
        'is_featured': True,
        'cancellation_terms': 'Full refund up to 14 days before departure.',
    }
)
if created:
    TourPricing.objects.create(tour=norway_tour, label='Adult', price=1150.00)
    TourMedia.objects.create(
        tour=norway_tour,
        file='destinations/tromso_Northern-Lights-by-minivan6-2-550x358.jpg',
        media_type='IMAGE',
        is_hero=True
    )
    print(f"[OK] Created Norway Tour: {norway_tour.title}")

# Sweden Tour: Stockholm Archipelago & Icehotel Adventure
sweden_tour, created = Tour.objects.get_or_create(
    slug='sweden-icehotel-kiruna-arctic-escape',
    defaults={
        'title': 'Swedish Lapland: Iconic Icehotel & Kiruna Aurora Camp',
        'short_summary': 'Sleep in hand-carved ice suites, experience reindeer sledding, and view auroras from Abisko Sky Station.',
        'overview': 'Discover the magic of Swedish Lapland. Stay at the world-famous Icehotel in Jukkasjärvi, explore the subarctic wilderness on snowshoes, and witness the northern lights from Abisko.',
        'destination': dest_map.get('kiruna-abisko', dest_map.get('stockholm')),
        'travel_style': style,
        'duration_band': band,
        'duration_text': '4 Days / 3 Nights',
        'status': 'PUBLISHED',
        'is_featured': True,
        'cancellation_terms': 'Full refund up to 14 days before departure.',
    }
)
if created:
    TourPricing.objects.create(tour=sweden_tour, label='Adult', price=990.00)
    TourMedia.objects.create(
        tour=sweden_tour,
        file='destinations/kiruna-abisko_31337_54406107252_f4ca19b35f_c_800_600_nofilter.jpg',
        media_type='IMAGE',
        is_hero=True
    )
    print(f"[OK] Created Sweden Tour: {sweden_tour.title}")

print("\n=== VERIFICATION ===")
for c in Country.objects.filter(is_active=True):
    d_count = c.destinations.count()
    t_count = Tour.objects.filter(destination__country=c, status='PUBLISHED').count()
    print(f"- {c.name}: {d_count} Destinations / Places | {t_count} Published Tour Packages")
