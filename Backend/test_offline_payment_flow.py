import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.test import Client
from decimal import Decimal
from tours.models import Tour, TourDate
from accounts.models import CustomUser
from bookings.models import Booking
from notifications.models import NotificationLog

print("=== STARTING OFFLINE PAYMENT INTEGRATION TEST ===")

# 1. Setup customer and tour
customer = CustomUser.objects.filter(role='CUSTOMER').first()
if not customer:
    customer = CustomUser.objects.create_user(
        username='offline_traveler',
        email='offline.traveler@nordvelocity.com',
        first_name='Elias',
        last_name='Virtanen',
        role='CUSTOMER'
    )

tour = Tour.objects.filter(status='PUBLISHED').first()
assert tour, "No published tour found"
tour_date = tour.dates.first()
if not tour_date:
    from datetime import date, timedelta
    tour_date = TourDate.objects.create(
        tour=tour,
        start_date=date.today() + timedelta(days=14),
        end_date=date.today() + timedelta(days=21),
        total_capacity=10,
        booked_count=0,
        status='AVAILABLE'
    )

client = Client()
client.force_login(customer)

# 2. Test booking creation via POST
create_res = client.post(f'/bookings/create/{tour.slug}/', {
    'date_id': tour_date.id,
    'adults': 2,
    'children': 0,
    'guest_adult_1_name': 'Elias Virtanen',
    'guest_adult_2_name': 'Aino Virtanen',
    'customer_notes': 'Please arrange winter thermal suits size L and M.'
}, follow=False)

assert create_res.status_code == 302, f"Expected 302 redirect, got {create_res.status_code}"
summary_url = create_res['Location']
booking_ref = summary_url.strip('/').split('/')[-1]
print(f"PASS: Tour Booking Created! Ref: {booking_ref}")

booking = Booking.objects.get(booking_ref=booking_ref)
initial_amount = booking.total_amount
print(f"Initial Booking Total: €{initial_amount}")

# 3. Test applying Coupon on summary page
coupon_res = client.post(f'/bookings/summary/{booking_ref}/', {
    'coupon_code': 'WINTER2026',
    'apply_coupon': '1'
}, follow=True)
assert coupon_res.status_code == 200
booking.refresh_from_db()
print(f"PASS: Applied Coupon WINTER2026. Discount: €{booking.discount_amount} | New Total: €{booking.total_amount}")
assert booking.discount_amount > 0, "Discount was not applied"

# 4. Test Offline Payment Submission (Pay on Arrival)
offline_res = client.post(f'/payments/offline/{booking.id}/', {
    'offline_method': 'OFFLINE',
    'customer_payment_notes': 'Will pay cash in EUR at Rovaniemi airport.'
}, follow=True)

assert offline_res.status_code == 200
booking.refresh_from_db()

print(f"PASS: Offline Payment Processed!")
print(f" - Payment Method: {booking.payment_method} ({booking.get_payment_method_display()})")
print(f" - Payment Status: {booking.payment_status} ({booking.get_payment_status_display()})")
print(f" - Booking Status: {booking.status} ({booking.get_status_display()})")

assert booking.payment_method == 'OFFLINE'
assert booking.payment_status == 'UNPAID'
assert booking.status == 'CONFIRMED'

# 5. Verify email notification recorded
last_log = NotificationLog.objects.filter(booking=booking).last()
assert last_log, "No notification log created for offline payment"
print(f"PASS: Email Notification Dispatched! Template: '{last_log.template.name}' to {last_log.recipient_email}")

# 6. Verify Booking Success Template rendered with offline instructions
html = offline_res.content.decode('utf-8')
assert 'Your Trip is Secured!' in html or 'Reservation Confirmed' in html
assert booking.booking_ref in html
assert 'Offline Payment' in html or 'Pay on Arrival' in html
print("PASS: Booking Success Page Rendered with Offline Instructions!")

# 7. Test Admin Reconciliation Action
admin_user = CustomUser.objects.filter(is_superuser=True).first()
admin_client = Client()
admin_client.force_login(admin_user)

changelist_res = admin_client.get('/admin/bookings/booking/')
assert changelist_res.status_code == 200
assert booking.booking_ref in changelist_res.content.decode('utf-8')
print("PASS: Admin Changelist displays the Offline Booking!")

# Mark as paid via Admin action
action_res = admin_client.post('/admin/bookings/booking/', {
    'action': 'mark_as_paid',
    '_selected_action': [booking.id],
}, follow=True)
assert action_res.status_code == 200

booking.refresh_from_db()
print(f"PASS: Admin marked as Paid! Payment Status: {booking.payment_status}")
assert booking.payment_status == 'PAID'

print("\n=== ALL OFFLINE PAYMENT TESTS PASSED 100% SUCCESSFULLY! ===")
