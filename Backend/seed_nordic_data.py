import os
import django
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from tours.models import (
    Country, Destination, TravelStyle, ExperienceType, Season, DurationBand,
    Tour, TourPricing, TourDate, TourHighlight, TourItinerary, TourInclusion, TourFAQ
)
from chauffeur.models import VehicleClass, Vehicle, PricingRule, FixedRoute
from payments.models import Coupon
from content.models import BlogPost, BlogCategory, BlogTag
from accounts.models import CustomUser

print("--- SEEDING NORD VELOCITY REALISTIC DATA ---")

# 1. Admin / Staff User
admin_user = CustomUser.objects.filter(is_superuser=True).first()
if not admin_user:
    admin_user = CustomUser.objects.create_superuser('admin', 'admin@nordvelocity.com', 'admin123')
    print("Created superuser admin@nordvelocity.com")

# 2. Countries & Destinations
finland, _ = Country.objects.get_or_create(slug='finland', defaults={'name': 'Finland', 'is_active': True, 'sort_order': 1})
norway, _ = Country.objects.get_or_create(slug='norway', defaults={'name': 'Norway', 'is_active': True, 'sort_order': 2})
sweden, _ = Country.objects.get_or_create(slug='sweden', defaults={'name': 'Sweden', 'is_active': True, 'sort_order': 3})

dest_rovaniemi, _ = Destination.objects.get_or_create(
    country=finland, slug='rovaniemi',
    defaults={'name': 'Rovaniemi', 'description': 'The Official Hometown of Santa Claus & Gateway to the Arctic Circle in Finnish Lapland.', 'is_active': True, 'sort_order': 1}
)
dest_helsinki, _ = Destination.objects.get_or_create(
    country=finland, slug='helsinki',
    defaults={'name': 'Helsinki', 'description': 'Nordic capital of architecture, coastal design, and vibrant culinary culture.', 'is_active': True, 'sort_order': 2}
)
dest_levi, _ = Destination.objects.get_or_create(
    country=finland, slug='levi',
    defaults={'name': 'Levi', 'description': 'Laplands premier ski wonderland with world-class slopes, husky safaris, and snowmobiling.', 'is_active': True, 'sort_order': 3}
)
dest_lakeland, _ = Destination.objects.get_or_create(
    country=finland, slug='lakeland',
    defaults={'name': 'Finnish Lakeland', 'description': 'Europe’s largest lake district featuring pristine blue waters, lakeside villas, and authentic wood saunas.', 'is_active': True, 'sort_order': 4}
)
dest_inari, _ = Destination.objects.get_or_create(
    country=finland, slug='inari-saariselka',
    defaults={'name': 'Inari & Saariselkä', 'description': 'Heart of indigenous Sámi culture, pristine national parks, and prime Aurora Borealis skies.', 'is_active': True, 'sort_order': 5}
)
print("Destinations seeded.")

# 3. Taxonomies
style_luxury, _ = TravelStyle.objects.get_or_create(name='Luxury & VIP', slug='luxury-vip')
style_adventure, _ = TravelStyle.objects.get_or_create(name='Arctic Adventure', slug='arctic-adventure')
style_family, _ = TravelStyle.objects.get_or_create(name='Family & Leisure', slug='family-leisure')

exp_aurora, _ = ExperienceType.objects.get_or_create(name='Northern Lights', slug='northern-lights')
exp_winter, _ = ExperienceType.objects.get_or_create(name='Winter Sports', slug='winter-sports')
exp_wellness, _ = ExperienceType.objects.get_or_create(name='Sauna & Wellness', slug='sauna-wellness')

season_winter, _ = Season.objects.get_or_create(slug='winter-2026', defaults={'name': 'Winter 2026', 'sort_order': 1})
season_summer, _ = Season.objects.get_or_create(slug='summer-2026', defaults={'name': 'Midnight Sun 2026', 'sort_order': 2})

# 4. Realistic Nordic Tours
tours_data = [
    {
        'title': 'Lapland Northern Lights & Glass Igloo Escape',
        'slug': 'lapland-northern-lights-glass-igloo-escape',
        'dest': dest_rovaniemi,
        'style': style_luxury,
        'days': 5,
        'price': Decimal('1250.00'),
        'featured': True,
        'summary': 'Immerse yourself in Finnish Lapland with overnight stays in heated glass igloos, reindeer sleigh rides, and guided Aurora chases.',
        'overview': 'Experience the magic of the Arctic Circle. Watch the Northern Lights dance directly above your bed through the panoramic glass dome. Includes private husky safaris, traditional fireside Lappish dinners, and personal photography guide.',
        'highlights': ['Stay in panoramic luxury glass igloo', 'Guided Aurora hunt with professional Arctic photographer', 'Private 10km husky dog sledding experience', 'Visit to Santa Claus Secret Forest'],
        'itinerary': [
            (1, 'Arrival in Rovaniemi & VIP Igloo Check-in', 'Private executive transfer to your luxury glass igloo resort followed by a welcome 3-course Arctic dinner.'),
            (2, 'Husky Safari & Wilderness Campfire', 'Drive your own husky team through snow-covered pine forests, followed by traditional berry tea by the open fire.'),
            (3, 'Reindeer Farm Visit & Sámi Traditions', 'Meet local reindeer herders, enjoy a peaceful sleigh ride, and learn about centuries of Arctic survival.'),
            (4, 'Snowmobile Aurora Expedition', 'Ride high-powered snowmobiles across frozen lakes away from city light pollution to chase the Aurora Borealis.'),
            (5, 'Farewell Lapland & Departure', 'Morning relaxing in Finnish sauna before your executive transfer to Rovaniemi Airport.')
        ]
    },
    {
        'title': 'Levi Arctic Adventure: Snowmobiling & Husky Safari',
        'slug': 'levi-arctic-adventure-snowmobile-husky',
        'dest': dest_levi,
        'style': style_adventure,
        'days': 4,
        'price': Decimal('790.00'),
        'featured': True,
        'summary': 'An adrenaline-packed winter escape through the fells of Levi featuring deep snow snowmobiling and dog sledding.',
        'overview': 'Designed for thrill-seekers, this package takes you deep into the pristine wilderness of Western Lapland. Experience breathtaking mountain views from fell summits and cozy evenings in timber chalets.',
        'highlights': ['Summit snowmobile trek with fell panoramic views', 'Speedy husky dog sledding through snow corridors', 'Traditional smoke sauna & snow dipping experience', 'Ski pass for Levi mountain'],
        'itinerary': [
            (1, 'Arrival at Kittilä & Levi Chalet Check-in', 'Meet & greet at Kittilä Airport with transfer to Levi Alpine Village.'),
            (2, 'Wilderness Snowmobile Tour', 'Ascend the Levi fells for panoramic views stretching across the Arctic horizon.'),
            (3, 'Husky Sledding & Evening Northern Lights Hunt', 'Musher masterclass and evening excursion in search of green auroral arcs.'),
            (4, 'Sauna Relaxation & Departure', 'Soak in the restorative heat of an authentic wood sauna before airport transfer.')
        ]
    },
    {
        'title': 'Finnish Lakeland Luxury Sauna & Villa Retreat',
        'slug': 'finnish-lakeland-luxury-sauna-villa-retreat',
        'dest': dest_lakeland,
        'style': style_luxury,
        'days': 4,
        'price': Decimal('890.00'),
        'featured': False,
        'summary': 'Unwind in a private architect-designed lakeside villa with private sauna, chef dining, and serene lake cruises.',
        'overview': 'Discover why Finland is the happiest country in the world. Immerse in the slow-paced luxury of Finnish Lakeland. Enjoy morning dips in crystal-clear waters, private sauna rituals, and local farm-to-table gastronomy.',
        'highlights': ['Private 5-star architect lakeside villa', 'Exclusive smoke sauna with certified Sauna Master', 'Private electric boat cruise on Lake Saimaa', 'Foraging wild Arctic berries & mushrooms with chef'],
        'itinerary': [
            (1, 'Arrival in Lakeland & Villa Welcome', 'Chauffeur transfer from Helsinki or Kuopio directly to your private lake estate.'),
            (2, 'Sauna Master Ritual & Ice/Lake Bathing', 'Experience the healing culture of Finnish Löyly guided by an authentic master.'),
            (3, 'Lake Saimaa Wildlife Cruise', 'Search for the rare Saimaa ringed seal on a quiet eco-boat cruise.'),
            (4, 'Gourmet Brunch & Return Transfer', 'Organic forest brunch before returning refreshed to Helsinki.')
        ]
    },
    {
        'title': 'Helsinki Archipelago & Modern Nordic Design Journey',
        'slug': 'helsinki-archipelago-nordic-design-journey',
        'dest': dest_helsinki,
        'style': style_family,
        'days': 3,
        'price': Decimal('490.00'),
        'featured': True,
        'summary': 'Explore the dynamic seaside capital, UNESCO fortress island of Suomenlinna, and world-renowned design district.',
        'overview': 'Experience the seamless blend of urban sophistication and wild coastal nature in Helsinki. Includes visits to the iconic Oodi Central Library, Amos Rex art museum, and a private RIB boat cruise through the Helsinki Archipelago.',
        'highlights': ['Private guided architecture & design district tour', 'Ferry excursion to UNESCO Suomenlinna sea fortress', 'VIP reservation at Löyly seaside sauna complex', 'Gourmet dinner at Michelin-selected restaurant'],
        'itinerary': [
            (1, 'Welcome to the Capital of Cool', 'Executive transfer from Helsinki-Vantaa Airport. Afternoon architectural walking tour.'),
            (2, 'Suomenlinna Fortress & Archipelago Cruise', 'Maritime journey to the historical sea fortress and coastal islands.'),
            (3, 'Design District Shopping & Departure', 'Browse premier Finnish design houses (Marimekko, Iittala, Artek) before airport departure.')
        ]
    }
]

band_multi, _ = DurationBand.objects.get_or_create(slug='multi-day', defaults={'name': 'Multi-Day Tours', 'min_hours': 48, 'max_hours': 240})

for td in tours_data:
    tour, created = Tour.objects.get_or_create(
        slug=td['slug'],
        defaults={
            'title': td['title'],
            'destination': td['dest'],
            'travel_style': td['style'],
            'duration_band': band_multi,
            'duration_text': f"{td['days']} Days / {td['days']-1} Nights",
            'status': 'PUBLISHED',
            'is_featured': td['featured'],
            'short_summary': td['summary'],
            'overview': td['overview'],
            'cancellation_terms': 'Full refund up to 30 days prior to departure. 50% refund between 14 to 29 days.',
        }
    )
    # Add seasons and experience types
    tour.seasons.add(season_winter)
    tour.experience_types.add(exp_aurora)

    # Pricing
    TourPricing.objects.get_or_create(
        tour=tour, label='Adult',
        defaults={'price': td['price'], 'currency': 'EUR', 'min_quantity': 1}
    )
    TourPricing.objects.get_or_create(
        tour=tour, label='Child',
        defaults={'price': (td['price'] * Decimal('0.5')).quantize(Decimal('0.01')), 'currency': 'EUR', 'min_quantity': 0}
    )

    # Dates (weekly for the next 8 weeks)
    today = date.today()
    for week in range(1, 9):
        dep_date = today + timedelta(days=week * 7)
        TourDate.objects.get_or_create(
            tour=tour, start_date=dep_date,
            defaults={'total_capacity': 12, 'booked_count': 2, 'status': 'AVAILABLE'}
        )

    # Highlights
    for i, hl in enumerate(td['highlights']):
        TourHighlight.objects.get_or_create(tour=tour, text=hl, defaults={'sort_order': i})

    # Itinerary
    for day_num, day_title, day_desc in td['itinerary']:
        TourItinerary.objects.get_or_create(
            tour=tour, day_number=day_num,
            defaults={'title': day_title, 'description': day_desc, 'sort_order': day_num}
        )

    # Inclusions
    TourInclusion.objects.get_or_create(tour=tour, text='Luxury Accommodation with Daily Breakfast', defaults={'is_included': True})
    TourInclusion.objects.get_or_create(tour=tour, text='Private Airport & Activity Transfers', defaults={'is_included': True})
    TourInclusion.objects.get_or_create(tour=tour, text='Professional English-Speaking Guide & Driver', defaults={'is_included': True})
    TourInclusion.objects.get_or_create(tour=tour, text='Thermal Winter Gear (Overalls, Boots, Gloves)', defaults={'is_included': True})
    TourInclusion.objects.get_or_create(tour=tour, text='International Flights', defaults={'is_included': False})

    # FAQs
    TourFAQ.objects.get_or_create(
        tour=tour, question='What should I pack for the winter tour?',
        defaults={'answer': 'We provide heavy-duty thermal outer overalls and winter boots for all activities. We recommend wearing thermal merino wool base layers and fleece sweaters underneath.'}
    )
    TourFAQ.objects.get_or_create(
        tour=tour, question='What is the cancellation policy?',
        defaults={'answer': 'Full refund up to 30 days prior to departure. 50% refund between 14 to 29 days. Comprehensive travel insurance is strongly recommended.'}
    )

print("Tours, dates, pricing, itineraries, and inclusions seeded.")

# 5. Chauffeur Fleet & Fixed Routes
vc_first, _ = VehicleClass.objects.get_or_create(
    slug='first-class-vip',
    defaults={'name': 'First Class VIP', 'description': 'The pinnacle of luxury travel. Mercedes-Benz S-Class or BMW 7 Series with executive reclining seats.', 'is_active': True, 'sort_order': 1}
)
PricingRule.objects.get_or_create(
    vehicle_class=vc_first,
    defaults={'base_fare': Decimal('40.00'), 'per_km_rate': Decimal('3.20'), 'per_minute_rate': Decimal('0.80'), 'minimum_fare': Decimal('60.00'), 'hourly_rate': Decimal('140.00'), 'valid_from': timezone.now(), 'is_active': True}
)

Vehicle.objects.get_or_create(
    name='Mercedes-Benz S-Class (S 580e)',
    vehicle_class=vc_first,
    defaults={'passenger_capacity': 3, 'luggage_capacity': 3, 'features': {'wifi': True, 'water': True, 'massage_seats': True, 'leather': True}, 'is_active': True}
)

vc_van, _ = VehicleClass.objects.get_or_create(
    slug='executive-van',
    defaults={'name': 'Executive Van', 'description': 'Spacious VIP travel for delegations and families. Mercedes-Benz V-Class Extra Long.', 'is_active': True, 'sort_order': 2}
)
PricingRule.objects.get_or_create(
    vehicle_class=vc_van,
    defaults={'base_fare': Decimal('45.00'), 'per_km_rate': Decimal('3.50'), 'per_minute_rate': Decimal('0.90'), 'minimum_fare': Decimal('70.00'), 'hourly_rate': Decimal('160.00'), 'valid_from': timezone.now(), 'is_active': True}
)
Vehicle.objects.get_or_create(
    name='Mercedes-Benz V-Class (V 300d Extra Long)',
    vehicle_class=vc_van,
    defaults={'passenger_capacity': 7, 'luggage_capacity': 7, 'features': {'wifi': True, 'water': True, 'conference_table': True, 'leather': True}, 'is_active': True}
)

vc_biz, _ = VehicleClass.objects.get_or_create(
    slug='business-class',
    defaults={'name': 'Business Class', 'description': 'Refined, discreet executive transfer. Mercedes-Benz E-Class / EQE all-electric.', 'is_active': True, 'sort_order': 3}
)
PricingRule.objects.get_or_create(
    vehicle_class=vc_biz,
    defaults={'base_fare': Decimal('25.00'), 'per_km_rate': Decimal('2.50'), 'per_minute_rate': Decimal('0.60'), 'minimum_fare': Decimal('45.00'), 'hourly_rate': Decimal('100.00'), 'valid_from': timezone.now(), 'is_active': True}
)
Vehicle.objects.get_or_create(
    name='Mercedes-Benz EQE Electric',
    vehicle_class=vc_biz,
    defaults={'passenger_capacity': 3, 'luggage_capacity': 2, 'features': {'wifi': True, 'water': True, 'leather': True, 'zero_emission': True}, 'is_active': True}
)


# Popular Fixed Transfer Routes
FixedRoute.objects.get_or_create(
    slug='helsinki-airport-city-center',
    defaults={
        'name': 'Helsinki Airport to City Center',
        'vehicle_class': vc_first,
        'origin_name': 'Helsinki-Vantaa Airport (HEL)',
        'origin_lat': Decimal('60.3172'), 'origin_lng': Decimal('24.9633'),
        'destination_name': 'Helsinki Central Hotel District',
        'destination_lat': Decimal('60.1699'), 'destination_lng': Decimal('24.9384'),
        'distance_km': Decimal('20.5'), 'estimated_duration_min': 25,
        'fixed_price': Decimal('85.00'), 'return_price': Decimal('150.00'), 'is_active': True
    }
)
FixedRoute.objects.get_or_create(
    slug='rovaniemi-airport-santa-village',
    defaults={
        'name': 'Rovaniemi Airport to Santa Claus Village',
        'vehicle_class': vc_van,
        'origin_name': 'Rovaniemi Airport (RVN)',
        'origin_lat': Decimal('66.5648'), 'origin_lng': Decimal('25.8304'),
        'destination_name': 'Santa Claus Village & Arctic TreeHouse',
        'destination_lat': Decimal('66.5436'), 'destination_lng': Decimal('25.8474'),
        'distance_km': Decimal('8.0'), 'estimated_duration_min': 10,
        'fixed_price': Decimal('55.00'), 'return_price': Decimal('100.00'), 'is_active': True
    }
)
FixedRoute.objects.get_or_create(
    slug='kittila-airport-levi-resort',
    defaults={
        'name': 'Kittilä Airport to Levi Ski Resort',
        'vehicle_class': vc_van,
        'origin_name': 'Kittilä Airport (KTT)',
        'origin_lat': Decimal('67.7010'), 'origin_lng': Decimal('24.8468'),
        'destination_name': 'Levi Alpine Village & Chalets',
        'destination_lat': Decimal('67.8048'), 'destination_lng': Decimal('24.8016'),
        'distance_km': Decimal('15.0'), 'estimated_duration_min': 18,
        'fixed_price': Decimal('75.00'), 'return_price': Decimal('140.00'), 'is_active': True
    }
)


print("Chauffeur fleet and fixed routes seeded.")

# 6. Coupons
Coupon.objects.get_or_create(
    code='WINTER2026',
    defaults={'discount_type': 'PERCENT', 'discount_value': Decimal('10.00'), 'min_order_amount': Decimal('500.00'), 'max_uses': 100, 'used_count': 5, 'valid_from': timezone.now(), 'valid_until': timezone.now() + timedelta(days=365), 'applicable_to': 'TOUR', 'is_active': True}
)
Coupon.objects.get_or_create(
    code='WELCOME50',
    defaults={'discount_type': 'FIXED', 'discount_value': Decimal('50.00'), 'min_order_amount': Decimal('200.00'), 'max_uses': 500, 'used_count': 12, 'valid_from': timezone.now(), 'valid_until': timezone.now() + timedelta(days=365), 'applicable_to': 'BOTH', 'is_active': True}
)

print("Promotions & Coupons seeded.")

# 7. Blog Posts
cat_guides, _ = BlogCategory.objects.get_or_create(name='Arctic Travel Guides', slug='arctic-travel-guides')
cat_culture, _ = BlogCategory.objects.get_or_create(name='Nordic Culture', slug='nordic-culture')

tag_aurora, _ = BlogTag.objects.get_or_create(name='Northern Lights', slug='northern-lights')
tag_sauna, _ = BlogTag.objects.get_or_create(name='Sauna', slug='sauna')

blog1, _ = BlogPost.objects.get_or_create(
    slug='how-to-see-the-northern-lights-lapland-guide',
    defaults={
        'title': 'How to Chase the Northern Lights in Lapland: The Complete 2026 Guide',
        'author': admin_user,
        'excerpt': 'Everything you need to know about witnessing the Aurora Borealis in Finland: best months, dark sky locations, and camera settings.',
        'body': 'The Northern Lights (Aurora Borealis) are among nature’s most awe-inspiring spectacles. In Finnish Lapland, the lights appear on roughly 200 nights a year between September and April. To maximize your chances, travel north of the Arctic Circle to Rovaniemi, Inari, or Saariselkä, away from artificial lights. Our guided minivan expeditions take travelers deep into the Arctic wilderness to scout cloud-free skies.',
        'status': 'PUBLISHED',
        'publish_date': date.today()
    }
)
blog1.categories.add(cat_guides)
blog1.tags.add(tag_aurora)

blog2, _ = BlogPost.objects.get_or_create(
    slug='the-sacred-art-of-the-finnish-sauna',
    defaults={
        'title': 'The Sacred Art of the Finnish Sauna: Why Every Traveler Must Experience Löyly',
        'author': admin_user,
        'excerpt': 'With over 3 million saunas for a population of 5.5 million, the sauna is the beating heart of Finnish lifestyle and wellbeing.',
        'body': 'In Finland, the sauna is not a luxury—it is an essential part of life. From rustic wood-fired lakeside cabins to urban design complexes like Löyly in Helsinki, taking a sauna cleanses both body and mind. The word Löyly refers to the warm steam that rises when water hits the hot stones. Follow it with an ice-cold plunge in a frozen lake for the ultimate Nordic endorphin rush.',
        'status': 'PUBLISHED',
        'publish_date': date.today()
    }
)
blog2.categories.add(cat_culture)
blog2.tags.add(tag_sauna)

print("Blog posts and categories seeded.")
print("=== NORD VELOCITY SEEDING COMPLETE! ===")
