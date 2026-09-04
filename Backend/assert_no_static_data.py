import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser

client = Client()
user = CustomUser.objects.filter(role='SUPERADMIN').first()
if user:
    client.force_login(user)

forbidden_strings = [
    'loremflickr',
    'WagonR',
    'Indica',
    'Dzire',
    'Innova Crysta',
    '36 new resort, New York',
    'street profit, New York',
    'Dependent on so extremely delivered by',
    'Whatever boy her exertion his extended',
    'Ecstatic followed handsome drawings',
]

urls_to_check = [
    '/',
    '/about/',
    '/faq/',
    '/contact/',
    '/tours/',
    '/tours/destinations/',
    '/tours/lapland-northern-lights-glass-igloo-escape/',
    '/transport/',
    '/transport/vehicles/',
    '/blog/',
    '/blog/how-to-see-the-northern-lights-lapland-guide/',
    '/accounts/dashboard/',
    '/accounts/my-bookings/',
    '/accounts/my-wishlist/',
    '/accounts/settings/',
]

print("=== ASSERTING ZERO STATIC / PLACEHOLDER STRINGS IN RENDERED HTML ===")
failures = 0
for url in urls_to_check:
    res = client.get(url, follow=True)
    html = res.content.decode('utf-8', errors='ignore')
    for bad in forbidden_strings:
        if bad.lower() in html.lower():
            print(f"FAIL: Found '{bad}' in {url}")
            failures += 1

if failures == 0:
    print("SUCCESS: 0 static/placeholder strings detected across all pages!")
else:
    print(f"FAILED: {failures} issues detected.")
    exit(1)
