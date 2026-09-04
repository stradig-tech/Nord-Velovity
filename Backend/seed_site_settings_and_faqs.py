import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from core.models import SiteSetting, FAQItem, Testimonial

print("--- SEEDING SITE SETTINGS, FAQS & TESTIMONIALS ---")

# 1. Update or create SiteSetting
setting, _ = SiteSetting.objects.get_or_create(
    id=1,
    defaults={
        'site_name': 'Nord Velocity',
        'tagline': 'Exclusive Nordic Tours & VIP Chauffeur Services',
        'hero_title': 'Discover the Untamed Beauty of the Nordics',
        'hero_subtitle': 'Curated Arctic expeditions, glass igloo stays, and VIP chauffeur transfers across Finland and Scandinavia.',
        'contact_email': 'concierge@nordvelocity.com',
        'contact_phone': '+358 9 1234 567',
        'emergency_phone': '+358 40 987 6543',
        'office_address': 'Pohjoisesplanadi 33, 00100 Helsinki, Finland',
        'operating_hours': 'Mon - Sun: 08:00 - 22:00 EET',
        'default_currency': 'EUR',
        'currency_symbol': '€',
        'facebook_url': 'https://facebook.com/nordvelocity',
        'instagram_url': 'https://instagram.com/nordvelocity',
        'linkedin_url': 'https://linkedin.com/company/nordvelocity',
        'tripadvisor_url': 'https://tripadvisor.com',
        'footer_text': 'Nord Velocity is Scandinavia’s premier luxury travel designer, providing bespoke Arctic tours, private husky expeditions, and VIP chauffeur services across Finland and the Nordics.',
        'copyright_text': '© 2026 Nord Velocity Oy. All rights reserved.',
        'maintenance_mode': False
    }
)
print("Site settings saved in database.")

# 2. General FAQs
faqs_data = [
    {
        'category': 'GENERAL',
        'question': 'What languages do your private guides and chauffeurs speak?',
        'answer': 'All our chauffeurs and private tour guides are fluent in English and Finnish. German, French, Spanish, and Mandarin-speaking guides are available upon request.',
        'order': 1
    },
    {
        'category': 'TOURS',
        'question': 'When is the best time to see the Northern Lights (Aurora Borealis)?',
        'answer': 'The Aurora season in Finnish Lapland extends from late August through early April. Peak auroral activity typically occurs around the equinoxes in September/October and February/March.',
        'order': 2
    },
    {
        'category': 'TOURS',
        'question': 'Are thermal winter overalls and boots included in tour packages?',
        'answer': 'Yes, for all winter and Arctic expeditions, high-quality thermal overalls, specialized snow boots, wool socks, and heavy-duty mittens are provided for every guest.',
        'order': 3
    },
    {
        'category': 'CHAUFFEUR',
        'question': 'How does airport meet & greet service work for VIP chauffeur bookings?',
        'answer': 'Your chauffeur monitors your flight in real-time. Upon landing, they will greet you inside the arrivals terminal holding an iPad with your name or corporate logo, assist with all luggage, and escort you to your vehicle.',
        'order': 4
    },
    {
        'category': 'PAYMENT',
        'question': 'What payment methods do you accept?',
        'answer': 'We accept all major credit cards (Visa, MasterCard, American Express) securely processed via Stripe, Apple Pay, Google Pay, and SEPA direct bank transfers for corporate bookings.',
        'order': 5
    },
    {
        'category': 'PAYMENT',
        'question': 'What is your cancellation and refund policy?',
        'answer': 'Tours can be cancelled with a 100% full refund up to 30 days before departure. Chauffeur point-to-point transfers can be cancelled free of charge up to 24 hours in advance.',
        'order': 6
    },
]

for fd in faqs_data:
    FAQItem.objects.get_or_create(
        question=fd['question'],
        defaults={
            'category': fd['category'],
            'answer': fd['answer'],
            'sort_order': fd['order'],
            'is_published': True
        }
    )
print("FAQs saved in database.")

# 3. Testimonials
testimonials_data = [
    {
        'name': 'Lord & Lady Harrington',
        'location': 'London, United Kingdom',
        'tour': 'Lapland Northern Lights & Glass Igloo Escape',
        'rating': 5,
        'quote': 'An unforgettable journey. Watching the Aurora dancing across the Arctic sky from our glass igloo bed was magical. Nord Velocity’s private chauffeur and guide made the entire trip effortless.',
        'order': 1
    },
    {
        'name': 'Marcus & Elena Lindqvist',
        'location': 'Stockholm, Sweden',
        'tour': 'Levi Arctic Adventure',
        'rating': 5,
        'quote': 'The snowmobile trek across the fells and the private husky safari were world-class. Pristine equipment, top-tier hospitality, and the private lakeside sauna was heaven.',
        'order': 2
    },
    {
        'name': 'Alexander von Bernstorff',
        'location': 'Frankfurt, Germany',
        'tour': 'VIP Executive Chauffeur Service',
        'rating': 5,
        'quote': 'Punctual, spotless Mercedes S-Class, and a chauffeur who knew Helsinki inside out. Nord Velocity is our go-to partner for executive transfers in Scandinavia.',
        'order': 3
    }
]

for td in testimonials_data:
    Testimonial.objects.get_or_create(
        author_name=td['name'],
        defaults={
            'author_location': td['location'],
            'tour_name': td['tour'],
            'rating': td['rating'],
            'quote': td['quote'],
            'sort_order': td['order'],
            'is_featured': True
        }
    )
print("Testimonials saved in database.")
print("=== SETTINGS & FAQS SEEDING COMPLETE! ===")
