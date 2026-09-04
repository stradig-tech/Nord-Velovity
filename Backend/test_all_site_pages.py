import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser

admin = CustomUser.objects.filter(is_superuser=True).first()
c = Client()
c.force_login(admin)

urls = [
    ('/', 'Homepage'),
    ('/about/', 'About Us'),
    ('/faq/', 'FAQ Center'),
    ('/contact/', 'Contact Concierge'),
    ('/tours/', 'Tours Catalog'),
    ('/tours/destinations/', 'Destinations List'),
    ('/tours/lapland-northern-lights-glass-igloo-escape/', 'Tour Detail Page'),
    ('/transport/', 'VIP Chauffeur Hub'),
    ('/transport/vehicles/', 'Chauffeur Fleet List'),
    ('/blog/', 'Blog & Stories List'),
    ('/blog/how-to-see-the-northern-lights-lapland-guide/', 'Blog Detail Page'),
    ('/accounts/login/', 'Customer Login'),
    ('/accounts/signup/', 'Customer Signup'),
    ('/accounts/dashboard/', 'Customer Dashboard'),
    ('/accounts/my-bookings/', 'My Bookings'),
    ('/accounts/my-wishlist/', 'My Wishlist'),
    ('/accounts/settings/', 'Account Settings'),
    ('/admin/', 'Executive Admin Dashboard'),
    ('/admin/tours/tour/', 'Admin Tours List'),
    ('/admin/tours/tourdate/', 'Admin Tour Inventory & Dates'),
    ('/admin/tours/tourpricing/', 'Admin Tour Pricing'),
    ('/admin/bookings/booking/', 'Admin Bookings List'),
    ('/admin/chauffeur/vehicle/', 'Admin Fleet List'),
    ('/admin/core/sitesetting/1/change/', 'Admin Site Settings'),
    ('/custom-admin/', 'Custom Admin Dashboard'),
    ('/custom-admin/bookings/', 'Custom Admin Bookings'),
    ('/custom-admin/guests/', 'Custom Admin Guests'),
    ('/custom-admin/earnings/', 'Custom Admin Earnings'),
    ('/custom-admin/reviews/', 'Custom Admin Reviews'),
    ('/custom-admin/settings/', 'Custom Admin Settings'),
]

print("=== FULL SITE COMPREHENSIVE INTEGRITY TEST ===")
failures = []
for url, name in urls:
    res = c.get(url, follow=True)
    if res.status_code == 200:
        print(f"PASS [200] {name:32} -> {url}")
    else:
        print(f"FAIL [{res.status_code}] {name:32} -> {url}")
        failures.append((url, name, res.status_code))

if not failures:
    print("\nALL 28 CORE VIEWS & SUBPAGES PASSED WITH 200 OK!")
else:
    print(f"\n{len(failures)} PAGES FAILED!")
    exit(1)
