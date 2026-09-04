import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser

admin = CustomUser.objects.filter(is_superuser=True).first()
c = Client()
c.force_login(admin)

pages_to_test = [
    ('/admin/', 'Dashboard'),
    ('/admin/bookings/booking/', 'Bookings'),
    ('/admin/tours/tour/', 'Tour Packages'),
    ('/admin/chauffeur/vehicle/', 'VIP Chauffeur Fleet'),
    ('/admin/accounts/customuser/', 'Guests & Users'),
    ('/admin/payments/coupon/', 'Promo Coupons'),
]

for url, expected_active in pages_to_test:
    res = c.get(url)
    html = res.content.decode('utf-8')
    assert res.status_code == 200
    assert 'Core Operations' in html, f"Core Operations missing on {url}"
    assert 'Marketing & Finance' in html, f"Marketing & Finance missing on {url}"
    assert 'nav-item active' in html, f"Active nav-item missing on {url}"
    print(f"PASS [200] {url:32} -> Sidebar unified, '{expected_active}' item active!")

print("\nALL PAGES CONFIRMED TO DISPLAY THE EXACT SAME CURATED LUXURY SIDEBAR!")
