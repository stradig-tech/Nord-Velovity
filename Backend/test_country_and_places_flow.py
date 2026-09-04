import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser

admin = CustomUser.objects.filter(is_superuser=True).first()
c = Client()
c.force_login(admin)

tests = [
    ('/', 'Finland'),
    ('/tours/country/finland/', 'Tour Places in Finland'),
    ('/tours/country/norway/', 'Tour Places in Norway'),
    ('/tours/country/sweden/', 'Tour Places in Sweden'),
    ('/tours/destinations/rovaniemi/', 'Tour Packages in Rovaniemi'),
    ('/tours/destinations/helsinki/', 'Tour Packages in Helsinki'),
    ('/tours/destinations/levi/', 'Tour Packages in Levi'),
    ('/tours/destinations/lakeland/', 'Tour Packages in Finnish Lakeland'),
    ('/tours/destinations/', 'Inspiring Tour Places'),
    ('/admin/tours/country/', 'Select country to change'),
    ('/admin/tours/destination/', 'Select destination to change'),
]

print("=== VERIFYING COUNTRY -> PLACES -> PACKAGES FLOW ===")
for url, expected_text in tests:
    res = c.get(url)
    assert res.status_code == 200, f"FAILED {url} with status {res.status_code}"
    html = res.content.decode('utf-8')
    assert expected_text in html, f"Missing '{expected_text}' in {url}"
    print(f"PASS [200] {url:35} -> Contains '{expected_text}'")

print("\nALL COUNTRY & DESTINATION FLOWS PASSED INTEGRITY TEST SUCCESSFULLY!")
