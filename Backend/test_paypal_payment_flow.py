import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nordvelocity.settings')
django.setup()

from django.test import Client
from decimal import Decimal
from tours.models import Tour, TourDate
from accounts.models import CustomUser
from bookings.models import Booking
from payments.models import PaymentIntent
from notifications.models import NotificationLog

print("=== STARTING PAYPAL INTEGRATION FLOW TEST ===")

# 1. Customer and Tour Setup
customer = CustomUser.objects.filter(role='CUSTOMER').first()
tour = Tour.objects.filter(status='PUBLISHED').first()
tour_date = tour.dates.first()

client = Client()
client.force_login(customer)

# 2. Create Tour Booking
create_res = client.post(f'/bookings/create/{tour.slug}/', {
    'date_id': tour_date.id,
    'adults': 1,
    'children': 0,
    'guest_adult_1_name': 'Matti Meikäläinen',
    'customer_notes': 'Booking with PayPal test.'
}, follow=False)

assert create_res.status_code == 302
summary_url = create_res['Location']
booking_ref = summary_url.strip('/').split('/')[-1]
print(f"PASS: Booking Created: {booking_ref}")

booking = Booking.objects.get(booking_ref=booking_ref)
print(f"Booking ID: {booking.id} | Amount: €{booking.total_amount}")

# 3. Test PayPal Order Creation Endpoint
create_order_res = client.get(f'/payments/paypal/create/{booking.id}/')
assert create_order_res.status_code == 200
data = create_order_res.json()
print("PayPal create_order response:", data)
assert data.get('success') is True
assert 'order_id' in data
assert 'approve_url' in data

order_id = data['order_id']
print(f"PASS: PayPal Order Created! Order ID: {order_id}")

# 4. Test PayPal Order Approval & Capture Endpoint
approve_res = client.get(f'/payments/paypal/approve/{booking.id}/?order_id={order_id}', follow=True)
assert approve_res.status_code == 200

booking.refresh_from_db()
print(f"PASS: PayPal Order Captured & Confirmed!")
print(f" - Payment Method: {booking.payment_method}")
print(f" - Payment Status: {booking.payment_status}")
print(f" - Booking Status: {booking.status}")

assert booking.payment_method == 'PAYPAL'
assert booking.payment_status == 'PAID'
assert booking.status == 'CONFIRMED'

# 5. Verify PaymentIntent record
pi = PaymentIntent.objects.filter(booking=booking, payment_method_type='paypal').first()
assert pi is not None
assert pi.status == 'SUCCEEDED'
print(f"PASS: PaymentIntent verified! Amount: €{pi.amount} | Status: {pi.status}")

# 6. Verify Customer Email Dispatched
notification = NotificationLog.objects.filter(booking=booking).last()
assert notification is not None
print(f"PASS: Email Notification logged for PayPal confirmation! Template: {notification.template.name}")

# 7. Verify Success Page rendered
html = approve_res.content.decode('utf-8')
assert 'Payment Successful' in html or 'Booking Confirmed' in html
assert booking.booking_ref in html
print("PASS: Customer Success Confirmation Page Rendered!")

print("\n=== ALL PAYPAL INTEGRATION TESTS PASSED 100% SUCCESSFULLY! ===")
