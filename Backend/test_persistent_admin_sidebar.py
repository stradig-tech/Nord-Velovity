import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser

admin = CustomUser.objects.filter(is_superuser=True).first()
c = Client()
c.force_login(admin)

urls = [
    '/admin/',
    '/admin/tours/tour/',
    '/admin/tours/tour/add/',
    '/admin/bookings/booking/',
    '/admin/tours/country/',
    '/admin/tours/destination/',
    '/admin/chauffeur/vehicle/',
    '/admin/accounts/customuser/',
]

for url in urls:
    res = c.get(url)
    assert res.status_code == 200, f"Failed {url} with {res.status_code}"
    html = res.content.decode('utf-8')
    assert 'id="nav-sidebar"' in html or 'admin-sidebar' in html, f"Missing nav-sidebar on {url}"
    assert 'Core Operations' in html, f"Missing Core Operations on {url}"
    assert 'nav_sidebar.css' not in html, f"Conflicting nav_sidebar.css found on {url}"
    print(f"PASS [200] {url:35} -> Persistent Executive Sidebar Present!")

print("\nALL ADMIN PAGES CONFIRMED TO RENDER THE PERSISTENT EXECUTIVE SIDEBAR!")
