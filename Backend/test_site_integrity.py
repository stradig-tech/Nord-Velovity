import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from tours.models import Tour, Departure, VehicleType, Wishlist
from channels.models import Channel

User = get_user_model()

def run_checks():
    client = Client()
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username="tempadmin", email="tempadmin@nordvelocity.test", password="temppassword123!"
        )

    public_urls = [
        '/',
        '/about/',
        '/faq/',
        '/contact/',
        '/tours/',
        '/transport/',
        '/blog/',
    ]

    print("\n--- 1. Testing Public URLs ---")
    for url in public_urls:
        resp = client.get(url)
        print(f"GET {url:20} -> {resp.status_code}")
        assert resp.status_code == 200, f"Expected 200 for {url}, got {resp.status_code}"

    print("\n--- 2. Testing Tour Detail & Booking URLs ---")
    first_tour = Tour.objects.filter(status='PUBLISHED').first()
    if first_tour:
        detail_url = f"/tours/{first_tour.slug}/"
        resp = client.get(detail_url)
        print(f"GET {detail_url:40} -> {resp.status_code}")
        assert resp.status_code == 200

        book_url = f"/bookings/create/{first_tour.slug}/"
        resp = client.get(book_url)
        print(f"GET {book_url:40} -> {resp.status_code}")
        assert resp.status_code == 200

        calc_url = f"/tours/api/{first_tour.id}/calculate-price/?adults=2&children=0"
        resp = client.get(calc_url)
        print(f"GET {calc_url:40} -> {resp.status_code}")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get('success') is True, f"API error: {data}"
        print(f"   Pricing: final_total = €{data['pricing']['final_total']}")

    print("\n--- 3. Testing Admin Hub & Calendar Endpoints ---")
    client.force_login(admin_user)

    admin_urls = [
        '/admin/',
        '/admin/operations/calendar/',
        '/admin/bookings/manual-create/',
        '/admin/bookings/booking/',
        '/admin/tours/departure/',
        '/admin/tours/vehicletype/',
        '/admin/channels/channel/',
        '/admin/channels/channelsynclog/',
        '/admin/api/departures/calendar/',
    ]

    for url in admin_urls:
        resp = client.get(url)
        print(f"GET {url:35} -> {resp.status_code}")
        assert resp.status_code == 200, f"Expected 200 for {url}, got {resp.status_code}"

    print("\n--- 4. Testing Live Departure Status Toggle API ---")
    first_dep = Departure.objects.first()
    if first_dep:
        toggle_url = f"/admin/api/departures/{first_dep.id}/status/"
        orig_status = first_dep.status
        resp = client.post(toggle_url, data='{"status": "BLOCKED"}', content_type='application/json')
        print(f"POST {toggle_url} -> {resp.status_code}")
        assert resp.status_code == 200
        first_dep.refresh_from_db()
        assert first_dep.status == "BLOCKED"
        print(f"   Status updated to: {first_dep.status}")

        # Restore original status
        client.post(toggle_url, data=f'{{"status": "{orig_status}"}}', content_type='application/json')
        first_dep.refresh_from_db()
        assert first_dep.status == orig_status
        print(f"   Status restored to: {first_dep.status}")

    print("\n--- 5. Testing Wishlist Feature Endpoints & Templates ---")
    if first_tour:
        # A. Unauthenticated toggle request -> 401 JSON
        unauth_client = Client()
        wish_url = f"/accounts/api/wishlist/toggle/{first_tour.id}/"
        resp = unauth_client.post(wish_url, content_type='application/json')
        print(f"POST {wish_url} (Guest) -> {resp.status_code}")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
        data = resp.json()
        assert data.get('login_required') is True
        print(f"   Guest redirected to: {data.get('login_url')}")

        # B. Authenticated toggle request -> Save
        Wishlist.objects.filter(user=admin_user).delete()
        resp = client.post(wish_url, content_type='application/json')
        print(f"POST {wish_url} (Auth user - save) -> {resp.status_code}")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get('success') is True
        assert data.get('is_saved') is True
        print(f"   Success: {data.get('message')}, total count = {data.get('count')}")

        # C. GET /accounts/my-wishlist/
        wishlist_page = client.get('/accounts/my-wishlist/')
        print(f"GET /accounts/my-wishlist/ -> {wishlist_page.status_code}")
        assert wishlist_page.status_code == 200
        assert first_tour.title.encode('utf-8') in wishlist_page.content or first_tour.slug.encode('utf-8') in wishlist_page.content
        print("   Tour appears on /accounts/my-wishlist/ successfully!")

        # D. Authenticated toggle request -> Remove
        resp = client.post(wish_url, content_type='application/json')
        print(f"POST {wish_url} (Auth user - remove) -> {resp.status_code}")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get('success') is True
        assert data.get('is_saved') is False
        print(f"   Success: {data.get('message')}, total count = {data.get('count')}")

    print("\n==============================================")
    print(" ALL SITE INTEGRITY & WISHLIST CHECKS PASSED WITH 200 OK!")
    print("==============================================\n")

if __name__ == '__main__':
    run_checks()

