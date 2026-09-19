from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, date, time
from decimal import Decimal

from accounts.models import CustomUser
from tours.models import (
    Country, Destination, Season, ExperienceType, TravelStyle, DurationBand,
    Tour, TourHighlight, TourItinerary, TourInclusion, TourFAQ,
    TourDate, TourPricing
)
from chauffeur.models import (
    VehicleClass, Vehicle, PricingRule, FixedRoute, Surcharge
)
from bookings.models import Booking, TourBooking, ChauffeurBooking, BookingStatusLog


class Command(BaseCommand):
    help = 'Seeds test data for Tours, Chauffeur, and Bookings'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Seeding test data...\n')

        # ──────────────────────────────────────────
        # 1. TAXONOMY (Tour categories)
        # ──────────────────────────────────────────
        self.stdout.write('  → Destinations...')
        
        # Countries (Parents)
        finland, _ = Destination.objects.get_or_create(name='Finland', slug='finland', defaults={'sort_order': 10, 'description': 'The land of a thousand lakes and Northern Lights.'})
        norway, _ = Destination.objects.get_or_create(name='Norway', slug='norway', defaults={'sort_order': 20, 'description': 'Fjords, majestic mountains, and northern lights.'})
        sweden, _ = Destination.objects.get_or_create(name='Sweden', slug='sweden', defaults={'sort_order': 30, 'description': 'Archipelagos, dense forests, and vibrant cities.'})
        denmark, _ = Destination.objects.get_or_create(name='Denmark', slug='denmark', defaults={'sort_order': 40, 'description': 'Historic cities, fairy tales, and beautiful coastlines.'})
        ireland, _ = Destination.objects.get_or_create(name='Ireland', slug='ireland', defaults={'sort_order': 50, 'description': 'The Emerald Isle, rich in history and folklore.'})

        # Cities / Locations (Children)
        helsinki, _ = Destination.objects.get_or_create(name='Helsinki', slug='helsinki', defaults={'sort_order': 1, 'description': 'Capital of Finland, vibrant city on the Baltic coast.', 'parent': finland})
        helsinki.parent = finland; helsinki.save()
        
        rovaniemi, _ = Destination.objects.get_or_create(name='Rovaniemi', slug='rovaniemi', defaults={'sort_order': 2, 'description': 'The official hometown of Santa Claus, gateway to Finnish Lapland.', 'parent': finland})
        rovaniemi.parent = finland; rovaniemi.save()
        
        levi, _ = Destination.objects.get_or_create(name='Levi', slug='levi', defaults={'sort_order': 3, 'description': 'Finland\'s largest ski resort and aurora viewing destination.', 'parent': finland})
        levi.parent = finland; levi.save()
        
        turku, _ = Destination.objects.get_or_create(name='Turku', slug='turku', defaults={'sort_order': 4, 'description': 'Historic former capital with medieval castle and archipelago.', 'parent': finland})
        turku.parent = finland; turku.save()
        
        tampere, _ = Destination.objects.get_or_create(name='Tampere', slug='tampere', defaults={'sort_order': 5, 'description': 'Industrial city known for its sauna culture and lakeside scenery.', 'parent': finland})
        tampere.parent = finland; tampere.save()

        self.stdout.write('  → Seasons...')
        winter, _ = Season.objects.get_or_create(name='Winter', slug='winter', defaults={'sort_order': 1})
        spring, _ = Season.objects.get_or_create(name='Spring', slug='spring', defaults={'sort_order': 2})
        summer, _ = Season.objects.get_or_create(name='Summer', slug='summer', defaults={'sort_order': 3})
        autumn, _ = Season.objects.get_or_create(name='Autumn', slug='autumn', defaults={'sort_order': 4})

        self.stdout.write('  → Experience Types...')
        northern_lights, _ = ExperienceType.objects.get_or_create(name='Northern Lights', slug='northern-lights', defaults={'sort_order': 1, 'description': 'Chase the aurora borealis across Lapland skies.'})
        nature, _ = ExperienceType.objects.get_or_create(name='Nature & Wildlife', slug='nature-wildlife', defaults={'sort_order': 2, 'description': 'Explore pristine forests, lakes, and Arctic wildlife.'})
        city_tour, _ = ExperienceType.objects.get_or_create(name='City Tour', slug='city-tour', defaults={'sort_order': 3, 'description': 'Discover Finland\'s vibrant cities and architecture.'})
        adventure, _ = ExperienceType.objects.get_or_create(name='Adventure', slug='adventure', defaults={'sort_order': 4, 'description': 'Husky safaris, snowmobile rides, and ice fishing.'})
        cultural, _ = ExperienceType.objects.get_or_create(name='Cultural', slug='cultural', defaults={'sort_order': 5, 'description': 'Finnish sauna traditions, local cuisine, and history.'})
        family, _ = ExperienceType.objects.get_or_create(name='Family', slug='family', defaults={'sort_order': 6, 'description': 'Kid-friendly experiences for the whole family.'})

        self.stdout.write('  → Travel Styles...')
        private, _ = TravelStyle.objects.get_or_create(name='Private', slug='private', defaults={'sort_order': 1})
        small_group, _ = TravelStyle.objects.get_or_create(name='Small Group', slug='small-group', defaults={'sort_order': 2})
        group, _ = TravelStyle.objects.get_or_create(name='Group', slug='group', defaults={'sort_order': 3})
        vip_style, _ = TravelStyle.objects.get_or_create(name='VIP', slug='vip', defaults={'sort_order': 4})

        self.stdout.write('  → Duration Bands...')
        half_day, _ = DurationBand.objects.get_or_create(name='Half Day', slug='half-day', defaults={'min_hours': 1, 'max_hours': 5, 'sort_order': 1})
        full_day, _ = DurationBand.objects.get_or_create(name='Full Day', slug='full-day', defaults={'min_hours': 6, 'max_hours': 12, 'sort_order': 2})
        multi_2, _ = DurationBand.objects.get_or_create(name='2-3 Days', slug='2-3-days', defaults={'min_hours': 24, 'max_hours': 72, 'sort_order': 3})
        multi_4, _ = DurationBand.objects.get_or_create(name='4-7 Days', slug='4-7-days', defaults={'min_hours': 96, 'max_hours': 168, 'sort_order': 4})

        # ──────────────────────────────────────────
        # 2. TOURS
        # ──────────────────────────────────────────
        self.stdout.write('\n  → Tours...')

        # Tour 1: Northern Lights Chase
        tour1, created = Tour.objects.get_or_create(
            slug='northern-lights-chase-rovaniemi',
            defaults={
                'title': 'Northern Lights Chase in Rovaniemi',
                'short_summary': 'Experience the magical aurora borealis with expert guides in Finnish Lapland.',
                'overview': 'Join our expert aurora hunters on a thrilling evening chase through the wilderness of Rovaniemi. We use real-time weather data and years of experience to find the best viewing spots away from light pollution. Hot drinks and warm suits provided.',
                'destination': rovaniemi,
                'travel_style': small_group,
                'duration_band': half_day,
                'duration_text': '4 Hours (Evening)',
                'meeting_point': 'Rovaniemi City Centre, Hotel Arctic Light',
                'transportation_info': 'Minibus transfer to aurora viewing site included.',
                'cancellation_terms': 'Free cancellation up to 24 hours before departure. No refund for no-shows.',
                'status': 'PUBLISHED',
                'is_featured': True,
                'sort_order': 1,
            }
        )
        if created:
            tour1.seasons.add(winter, autumn)
            tour1.experience_types.add(northern_lights, nature, adventure)
            TourHighlight.objects.create(tour=tour1, text='Professional aurora photography tips', sort_order=1)
            TourHighlight.objects.create(tour=tour1, text='Hot chocolate & snacks by campfire', sort_order=2)
            TourHighlight.objects.create(tour=tour1, text='Thermal suits & boots provided', sort_order=3)
            TourHighlight.objects.create(tour=tour1, text='Small group — max 12 guests', sort_order=4)
            TourItinerary.objects.create(tour=tour1, day_number=1, title='Evening: Departure & Chase', description='We pick you up from your hotel at 8:00 PM and head into the wilderness based on real-time aurora forecasts.', sort_order=1)
            TourItinerary.objects.create(tour=tour1, day_number=1, title='Night: Aurora Viewing', description='Arrive at a carefully selected spot, enjoy hot drinks, and watch the northern lights dance across the sky.', sort_order=2)
            TourInclusion.objects.create(tour=tour1, text='Hotel pickup & drop-off', is_included=True, sort_order=1)
            TourInclusion.objects.create(tour=tour1, text='Thermal suit & boots', is_included=True, sort_order=2)
            TourInclusion.objects.create(tour=tour1, text='Hot drinks & snacks', is_included=True, sort_order=3)
            TourInclusion.objects.create(tour=tour1, text='Meals / Dinner', is_included=False, sort_order=4)
            TourFAQ.objects.create(tour=tour1, question='What if the Northern Lights don\'t appear?', answer='Nature is unpredictable. If no aurora is visible, you can rebook for free within 7 days (subject to availability).', sort_order=1)
            TourFAQ.objects.create(tour=tour1, question='What should I wear?', answer='We provide thermal suits and boots. Bring warm base layers, gloves, and a hat.', sort_order=2)
            TourDate.objects.create(tour=tour1, start_date=date(2026, 12, 15), total_capacity=12, status='AVAILABLE')
            TourDate.objects.create(tour=tour1, start_date=date(2026, 12, 20), total_capacity=12, status='AVAILABLE')
            TourDate.objects.create(tour=tour1, start_date=date(2027, 1, 5), total_capacity=12, status='AVAILABLE')
            TourDate.objects.create(tour=tour1, start_date=date(2027, 1, 15), total_capacity=12, booked_count=12, status='SOLD_OUT')
            TourPricing.objects.create(tour=tour1, label='Adult', price=Decimal('149.00'), sort_order=1)
            TourPricing.objects.create(tour=tour1, label='Child (7-12)', price=Decimal('99.00'), sort_order=2)
            TourPricing.objects.create(tour=tour1, label='Private Group (up to 4)', price=Decimal('450.00'), sort_order=3)

        # Tour 2: Helsinki City Walking Tour
        tour2, created = Tour.objects.get_or_create(
            slug='helsinki-city-walking-tour',
            defaults={
                'title': 'Helsinki City Walking Tour',
                'short_summary': 'Discover Helsinki\'s iconic landmarks, hidden gems, and local culture on foot.',
                'overview': 'Walk through the heart of Finland\'s capital with a passionate local guide. Visit Senate Square, the Design District, Market Hall, and the stunning Temppeliaukio Rock Church. Learn about Finnish history, architecture, and daily life.',
                'destination': helsinki,
                'travel_style': group,
                'duration_band': half_day,
                'duration_text': '3 Hours',
                'meeting_point': 'Senate Square, Helsinki Cathedral steps',
                'cancellation_terms': 'Free cancellation up to 12 hours before departure.',
                'status': 'PUBLISHED',
                'is_featured': True,
                'sort_order': 2,
            }
        )
        if created:
            tour2.seasons.add(spring, summer, autumn)
            tour2.experience_types.add(city_tour, cultural)
            TourHighlight.objects.create(tour=tour2, text='Visit 10+ iconic Helsinki landmarks', sort_order=1)
            TourHighlight.objects.create(tour=tour2, text='Local guide with insider knowledge', sort_order=2)
            TourHighlight.objects.create(tour=tour2, text='Small groups for personal experience', sort_order=3)
            TourItinerary.objects.create(tour=tour2, day_number=1, title='Morning: Senate Square & Cathedral', description='Start at the iconic Helsinki Cathedral and learn about Finland\'s history.', sort_order=1)
            TourItinerary.objects.create(tour=tour2, day_number=1, title='Mid-morning: Design District', description='Walk through the trendy Design District, visit local shops and galleries.', sort_order=2)
            TourItinerary.objects.create(tour=tour2, day_number=1, title='Late Morning: Rock Church & Market Hall', description='Visit the stunning Temppeliaukio Church carved into rock, then taste local flavours at the Old Market Hall.', sort_order=3)
            TourInclusion.objects.create(tour=tour2, text='Expert local guide', is_included=True, sort_order=1)
            TourInclusion.objects.create(tour=tour2, text='Entry to Temppeliaukio Church', is_included=True, sort_order=2)
            TourInclusion.objects.create(tour=tour2, text='Food & drinks', is_included=False, sort_order=3)
            TourInclusion.objects.create(tour=tour2, text='Hotel transfers', is_included=False, sort_order=4)
            TourDate.objects.create(tour=tour2, start_date=date(2026, 10, 1), total_capacity=20, status='AVAILABLE')
            TourDate.objects.create(tour=tour2, start_date=date(2026, 10, 8), total_capacity=20, booked_count=18, status='AVAILABLE')
            TourDate.objects.create(tour=tour2, start_date=date(2026, 10, 15), total_capacity=20, status='AVAILABLE')
            TourPricing.objects.create(tour=tour2, label='Adult', price=Decimal('59.00'), sort_order=1)
            TourPricing.objects.create(tour=tour2, label='Child (7-12)', price=Decimal('29.00'), sort_order=2)
            TourPricing.objects.create(tour=tour2, label='Student', price=Decimal('45.00'), sort_order=3)

        # Tour 3: Lapland Husky Safari
        tour3, created = Tour.objects.get_or_create(
            slug='lapland-husky-safari-adventure',
            defaults={
                'title': 'Lapland Husky Safari Adventure',
                'short_summary': 'Mush your own team of huskies through pristine Arctic wilderness.',
                'overview': 'Experience the thrill of driving your own husky sled team through the snow-covered forests of Levi. Meet the dogs, learn mushing techniques from expert handlers, and glide through breathtaking winter landscapes. A once-in-a-lifetime Arctic adventure.',
                'destination': levi,
                'travel_style': private,
                'duration_band': full_day,
                'duration_text': '6 Hours',
                'meeting_point': 'Levi Husky Farm, Kittilä',
                'meal_info': 'Traditional Lappish lunch cooked over an open fire is included.',
                'transportation_info': 'Transfer from Levi centre hotels included.',
                'cancellation_terms': 'Free cancellation up to 48 hours before departure. 50% refund within 48 hours.',
                'status': 'PUBLISHED',
                'is_featured': True,
                'sort_order': 3,
            }
        )
        if created:
            tour3.seasons.add(winter)
            tour3.experience_types.add(adventure, nature, family)
            TourHighlight.objects.create(tour=tour3, text='Drive your own husky sled team', sort_order=1)
            TourHighlight.objects.create(tour=tour3, text='Meet & cuddle 200+ Alaskan huskies', sort_order=2)
            TourHighlight.objects.create(tour=tour3, text='Traditional Lappish lunch over campfire', sort_order=3)
            TourHighlight.objects.create(tour=tour3, text='20 km trail through Arctic wilderness', sort_order=4)
            TourItinerary.objects.create(tour=tour3, day_number=1, title='Morning: Arrival & Safety Briefing', description='Arrive at the husky farm, meet the dogs, and receive a safety briefing on mushing techniques.', sort_order=1)
            TourItinerary.objects.create(tour=tour3, day_number=1, title='Mid-day: The Safari', description='Hit the trail! Drive your own sled through forests and frozen lakes for approximately 20 km.', sort_order=2)
            TourItinerary.objects.create(tour=tour3, day_number=1, title='Afternoon: Lunch & Return', description='Enjoy a traditional Lappish lunch cooked over an open fire, then return to the farm.', sort_order=3)
            TourInclusion.objects.create(tour=tour3, text='Hotel pickup & drop-off from Levi', is_included=True, sort_order=1)
            TourInclusion.objects.create(tour=tour3, text='Full thermal clothing & boots', is_included=True, sort_order=2)
            TourInclusion.objects.create(tour=tour3, text='Lappish lunch & hot drinks', is_included=True, sort_order=3)
            TourInclusion.objects.create(tour=tour3, text='Gratuities', is_included=False, sort_order=4)
            TourFAQ.objects.create(tour=tour3, question='Do I need experience with dogs?', answer='No experience needed! Our guides will teach you everything before hitting the trail.', sort_order=1)
            TourFAQ.objects.create(tour=tour3, question='Is this suitable for children?', answer='Yes! Children aged 4+ can ride as passengers in the sled. Minimum age to drive a sled is 15.', sort_order=2)
            TourDate.objects.create(tour=tour3, start_date=date(2026, 12, 10), total_capacity=8, status='AVAILABLE')
            TourDate.objects.create(tour=tour3, start_date=date(2026, 12, 18), total_capacity=8, booked_count=6, status='AVAILABLE')
            TourDate.objects.create(tour=tour3, start_date=date(2027, 1, 8), total_capacity=8, status='AVAILABLE')
            TourDate.objects.create(tour=tour3, start_date=date(2027, 2, 14), total_capacity=8, status='AVAILABLE')
            TourPricing.objects.create(tour=tour3, label='Adult', price=Decimal('249.00'), sort_order=1)
            TourPricing.objects.create(tour=tour3, label='Child (4-12)', price=Decimal('149.00'), sort_order=2)

        # ──────────────────────────────────────────
        # 3. CHAUFFEUR (Vehicles & Pricing)
        # ──────────────────────────────────────────
        self.stdout.write('\n  → Vehicle Classes...')

        business, _ = VehicleClass.objects.get_or_create(
            slug='business',
            defaults={'name': 'Business Class', 'description': 'Premium sedans for comfortable business travel.', 'sort_order': 1}
        )
        first_class, _ = VehicleClass.objects.get_or_create(
            slug='first-class',
            defaults={'name': 'First Class', 'description': 'Luxury vehicles for the most discerning travellers.', 'sort_order': 2}
        )
        vip_class, _ = VehicleClass.objects.get_or_create(
            slug='vip',
            defaults={'name': 'VIP', 'description': 'Ultra-premium chauffeur experience with top-tier vehicles.', 'sort_order': 3}
        )
        van_class, _ = VehicleClass.objects.get_or_create(
            slug='van',
            defaults={'name': 'Van / Minibus', 'description': 'Spacious vehicles for groups and families.', 'sort_order': 4}
        )

        self.stdout.write('  → Vehicles...')
        Vehicle.objects.get_or_create(name='Mercedes E-Class', defaults={'vehicle_class': business, 'passenger_capacity': 3, 'luggage_capacity': 3, 'features': {'wifi': True, 'water': True, 'charger': True}})
        Vehicle.objects.get_or_create(name='BMW 5 Series', defaults={'vehicle_class': business, 'passenger_capacity': 3, 'luggage_capacity': 3, 'features': {'wifi': True, 'water': True, 'charger': True}})
        Vehicle.objects.get_or_create(name='Mercedes S-Class', defaults={'vehicle_class': first_class, 'passenger_capacity': 3, 'luggage_capacity': 3, 'features': {'wifi': True, 'water': True, 'charger': True, 'champagne': True}})
        Vehicle.objects.get_or_create(name='BMW 7 Series', defaults={'vehicle_class': first_class, 'passenger_capacity': 3, 'luggage_capacity': 3, 'features': {'wifi': True, 'water': True, 'charger': True, 'champagne': True}})
        Vehicle.objects.get_or_create(name='Mercedes-Maybach S-Class', defaults={'vehicle_class': vip_class, 'passenger_capacity': 2, 'luggage_capacity': 2, 'features': {'wifi': True, 'water': True, 'charger': True, 'champagne': True, 'privacy_partition': True}})
        Vehicle.objects.get_or_create(name='Mercedes V-Class', defaults={'vehicle_class': van_class, 'passenger_capacity': 7, 'luggage_capacity': 7, 'features': {'wifi': True, 'water': True, 'charger': True}})
        Vehicle.objects.get_or_create(name='Mercedes Sprinter', defaults={'vehicle_class': van_class, 'passenger_capacity': 14, 'luggage_capacity': 14, 'features': {'wifi': True, 'water': True}})

        self.stdout.write('  → Pricing Rules...')
        now = timezone.now()
        PricingRule.objects.get_or_create(vehicle_class=business, is_active=True, valid_from=now, defaults={'base_fare': Decimal('15.00'), 'per_km_rate': Decimal('2.50'), 'per_minute_rate': Decimal('0.50'), 'minimum_fare': Decimal('25.00'), 'hourly_rate': Decimal('65.00')})
        PricingRule.objects.get_or_create(vehicle_class=first_class, is_active=True, valid_from=now, defaults={'base_fare': Decimal('25.00'), 'per_km_rate': Decimal('3.50'), 'per_minute_rate': Decimal('0.75'), 'minimum_fare': Decimal('45.00'), 'hourly_rate': Decimal('95.00')})
        PricingRule.objects.get_or_create(vehicle_class=vip_class, is_active=True, valid_from=now, defaults={'base_fare': Decimal('50.00'), 'per_km_rate': Decimal('5.00'), 'per_minute_rate': Decimal('1.00'), 'minimum_fare': Decimal('80.00'), 'hourly_rate': Decimal('150.00')})
        PricingRule.objects.get_or_create(vehicle_class=van_class, is_active=True, valid_from=now, defaults={'base_fare': Decimal('20.00'), 'per_km_rate': Decimal('3.00'), 'per_minute_rate': Decimal('0.60'), 'minimum_fare': Decimal('35.00'), 'hourly_rate': Decimal('80.00')})

        self.stdout.write('  → Fixed Price Transfers...')
        FixedRoute.objects.get_or_create(slug='helsinki-airport-business', defaults={
            'name': 'Helsinki Airport Transfer', 'vehicle_class': business, 'transfer_type': 'AIRPORT',
            'pickup_name': 'Helsinki City Centre', 'pickup_lat': Decimal('60.169856'), 'pickup_lng': Decimal('24.938379'),
            'dropoff_name': 'Helsinki-Vantaa Airport', 'dropoff_lat': Decimal('60.317222'), 'dropoff_lng': Decimal('24.963333'),
            'distance_km': Decimal('22.50'), 'estimated_duration_min': 30, 'fixed_price': Decimal('55.00'),
            'is_return_available': True, 'return_price': Decimal('50.00')
        })
        FixedRoute.objects.get_or_create(slug='helsinki-airport-first', defaults={
            'name': 'Helsinki Airport Transfer', 'vehicle_class': first_class, 'transfer_type': 'AIRPORT',
            'pickup_name': 'Helsinki City Centre', 'pickup_lat': Decimal('60.169856'), 'pickup_lng': Decimal('24.938379'),
            'dropoff_name': 'Helsinki-Vantaa Airport', 'dropoff_lat': Decimal('60.317222'), 'dropoff_lng': Decimal('24.963333'),
            'distance_km': Decimal('22.50'), 'estimated_duration_min': 30, 'fixed_price': Decimal('85.00'),
            'is_return_available': True, 'return_price': Decimal('80.00')
        })
        FixedRoute.objects.get_or_create(slug='helsinki-airport-vip', defaults={
            'name': 'Helsinki Airport Transfer', 'vehicle_class': vip_class, 'transfer_type': 'AIRPORT',
            'pickup_name': 'Helsinki City Centre', 'pickup_lat': Decimal('60.169856'), 'pickup_lng': Decimal('24.938379'),
            'dropoff_name': 'Helsinki-Vantaa Airport', 'dropoff_lat': Decimal('60.317222'), 'dropoff_lng': Decimal('24.963333'),
            'distance_km': Decimal('22.50'), 'estimated_duration_min': 30, 'fixed_price': Decimal('150.00'),
            'is_return_available': True, 'return_price': Decimal('140.00')
        })

        self.stdout.write('  → Surcharges...')
        Surcharge.objects.get_or_create(name='Night Surcharge', defaults={
            'surcharge_category': 'NIGHT', 'amount': Decimal('15.00'), 'amount_type': 'FLAT',
            'start_time': time(22, 0), 'end_time': time(6, 0)
        })
        Surcharge.objects.get_or_create(name='Weekend Surcharge', defaults={
            'surcharge_category': 'WEEKEND', 'amount': Decimal('10.00'), 'amount_type': 'PERCENT',
            'applicable_days': [5, 6]
        })
        Surcharge.objects.get_or_create(name='Christmas Day', defaults={
            'surcharge_category': 'HOLIDAY', 'amount': Decimal('25.00'), 'amount_type': 'FLAT',
            'specific_date': date(2026, 12, 25)
        })

        # ──────────────────────────────────────────
        # 4. BOOKINGS (Sample records)
        # ──────────────────────────────────────────
        self.stdout.write('\n  → Sample Bookings...')

        # Get the first admin user as the test customer
        admin_user = CustomUser.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.WARNING('  ⚠ No superuser found — skipping bookings. Run createsuperuser first.'))
        else:
            # Get a vehicle and tour date for the bookings
            vehicle = Vehicle.objects.filter(name='Mercedes E-Class').first()
            tour1_date = TourDate.objects.filter(tour=tour1, status='AVAILABLE').first()
            tour3_date = TourDate.objects.filter(tour=tour3, status='AVAILABLE').first()

            # Booking 1: Confirmed Tour Booking
            b1, created = Booking.objects.get_or_create(
                booking_ref='NV-2026-00001',
                defaults={
                    'booking_type': 'TOUR', 'customer': admin_user, 'status': 'CONFIRMED',
                    'subtotal': Decimal('298.00'), 'total_amount': Decimal('298.00'), 'currency': 'EUR',
                    'customer_notes': 'We are celebrating our anniversary!',
                }
            )
            if created and tour1_date:
                TourBooking.objects.create(booking=b1, tour=tour1, tour_date=tour1_date, adults=2, children=0, total_guests=2)
                BookingStatusLog.objects.create(booking=b1, old_status='PENDING', new_status='CONFIRMED', changed_by=admin_user, reason='Payment confirmed via Stripe')

            # Booking 2: Completed Chauffeur Booking
            b2, created = Booking.objects.get_or_create(
                booking_ref='NV-2026-00002',
                defaults={
                    'booking_type': 'CHAUFFEUR', 'customer': admin_user, 'status': 'COMPLETED',
                    'subtotal': Decimal('55.00'), 'total_amount': Decimal('55.00'), 'currency': 'EUR',
                }
            )
            if created and vehicle:
                ChauffeurBooking.objects.create(
                    booking=b2, vehicle=vehicle,
                    pickup_address='Helsinki City Centre', pickup_lat=Decimal('60.169856'), pickup_lng=Decimal('24.938379'),
                    destination_address='Helsinki-Vantaa Airport', destination_lat=Decimal('60.317222'), destination_lng=Decimal('24.963333'),
                    pickup_datetime=timezone.now() - timedelta(days=3),
                    distance_km=Decimal('22.50'), estimated_duration_min=30,
                    quote_id='Q-2026-001', route_type='FIXED',
                    passenger_count=2, luggage_count=2,
                )
                BookingStatusLog.objects.create(booking=b2, old_status='PENDING', new_status='CONFIRMED', changed_by=admin_user, reason='Payment confirmed')
                BookingStatusLog.objects.create(booking=b2, old_status='CONFIRMED', new_status='COMPLETED', changed_by=admin_user, reason='Trip completed')

            # Booking 3: Pending Tour Booking
            b3, created = Booking.objects.get_or_create(
                booking_ref='NV-2026-00003',
                defaults={
                    'booking_type': 'TOUR', 'customer': admin_user, 'status': 'PENDING',
                    'subtotal': Decimal('547.00'), 'total_amount': Decimal('547.00'), 'currency': 'EUR',
                    'customer_notes': 'First time visiting Lapland, very excited!',
                }
            )
            if created and tour3_date:
                TourBooking.objects.create(booking=b3, tour=tour3, tour_date=tour3_date, adults=2, children=1, total_guests=3)

        # ──────────────────────────────────────────
        # DONE
        # ──────────────────────────────────────────
        tour_count = Tour.objects.count()
        vehicle_count = Vehicle.objects.count()
        booking_count = Booking.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Seeding complete!'
            f'\n   Tours: {tour_count} | Vehicles: {vehicle_count} | Bookings: {booking_count}'
            f'\n   Open http://127.0.0.1:8000/admin/ to see your data!'
        ))
