import datetime
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

from tours.models import (
    Country, Destination, TravelStyle, DurationBand, Tour, TourPricing, VehicleType,
    TourOptionPricing, Departure, DepartureCapacity
)
from tours.services import DepartureService
from bookings.models import Booking, TourBooking, GuaranteedReattempt
from bookings.services import BookingService
from channels.models import Channel, ChannelSyncLog
from channels.services import ChannelSyncService

User = get_user_model()


class OTAArchitectureAcceptanceTests(TestCase):
    """
    16-Point Developer Guide Acceptance Test Suite
    Validates central departure-based inventory, multi-vehicle capacity,
    cross-channel deduction, overbooking prevention, re-attempt management,
    and OTA sync failure alerts.
    """

    def setUp(self):
        # 1. Base Geo & Tour Setup
        self.country = Country.objects.create(name="Norway", slug="norway", is_active=True)
        self.destination = Destination.objects.create(
            country=self.country, name="Tromso", slug="tromso", is_active=True
        )
        self.travel_style = TravelStyle.objects.create(name="Aurora Adventure", slug="aurora-adventure")
        self.duration_band = DurationBand.objects.create(name="Half Day", slug="half-day", min_hours=4, max_hours=8)
        self.tour = Tour.objects.create(
            title="Northern Lights Ultimate Hunt",
            slug="northern-lights-hunt",
            short_summary="Witness the Arctic Aurora Borealis.",
            overview="An unforgettable journey through the Arctic wilderness chasing the northern lights.",
            destination=self.destination,
            travel_style=self.travel_style,
            duration_band=self.duration_band,
            duration_text="6 Hours",
            cancellation_terms="Free cancellation up to 15 days before departure.",
            status="PUBLISHED",
            has_guaranteed_reattempt=True
        )
        TourPricing.objects.create(tour=self.tour, label="Adult", price=150.00)
        TourPricing.objects.create(tour=self.tour, label="Child", price=75.00)

        # 2. Vehicle Types Setup: Private Car (4), Micro (12), Group Bus (54)
        self.vt_car, _ = VehicleType.objects.get_or_create(
            slug="private-car",
            defaults={"name": "Private Car", "category": "CAR", "default_capacity": 4, "price_multiplier": 1.30, "is_active": True}
        )
        self.vt_micro, _ = VehicleType.objects.get_or_create(
            slug="micro",
            defaults={"name": "Micro", "category": "MICRO", "default_capacity": 12, "price_multiplier": 1.00, "is_active": True}
        )
        self.vt_bus, _ = VehicleType.objects.get_or_create(
            slug="group-bus",
            defaults={"name": "Group Bus", "category": "BUS", "default_capacity": 54, "price_multiplier": 0.85, "is_active": True}
        )

        TourOptionPricing.objects.create(tour=self.tour, vehicle_type=self.vt_car, adult_price=195.00, child_price=95.00)
        TourOptionPricing.objects.create(tour=self.tour, vehicle_type=self.vt_micro, adult_price=150.00, child_price=75.00)
        TourOptionPricing.objects.create(tour=self.tour, vehicle_type=self.vt_bus, adult_price=125.00, child_price=60.00)

        # 3. Customer Setup (User instance)
        self.customer = User.objects.create_user(
            username="astrid",
            first_name="Astrid",
            last_name="Lindgren",
            email="astrid@nordvelocity.test",
            password="testpassword123"
        )

        # 4. Departures Setup: Day 1 and Day 2
        self.today = timezone.now().date() + datetime.timedelta(days=1)
        self.tomorrow = timezone.now().date() + datetime.timedelta(days=2)

        self.dep_day1 = Departure.objects.create(
            tour=self.tour,
            date=self.today,
            time=datetime.time(19, 0),
            status="OPEN"
        )
        self.cap_day1_car = DepartureCapacity.objects.create(
            departure=self.dep_day1, vehicle_type=self.vt_car, total_capacity=4
        )
        self.cap_day1_micro = DepartureCapacity.objects.create(
            departure=self.dep_day1, vehicle_type=self.vt_micro, total_capacity=12
        )
        self.cap_day1_bus = DepartureCapacity.objects.create(
            departure=self.dep_day1, vehicle_type=self.vt_bus, total_capacity=54
        )

        self.dep_day2 = Departure.objects.create(
            tour=self.tour,
            date=self.tomorrow,
            time=datetime.time(19, 0),
            status="OPEN"
        )
        self.cap_day2_car = DepartureCapacity.objects.create(
            departure=self.dep_day2, vehicle_type=self.vt_car, total_capacity=4
        )
        self.cap_day2_micro = DepartureCapacity.objects.create(
            departure=self.dep_day2, vehicle_type=self.vt_micro, total_capacity=12
        )
        self.cap_day2_bus = DepartureCapacity.objects.create(
            departure=self.dep_day2, vehicle_type=self.vt_bus, total_capacity=54
        )

        # 5. Superuser Setup
        self.admin_user = User.objects.create_superuser(
            username="nordadmin", email="admin@nordvelocity.com", password="SecureNordPassword123!"
        )

    # Test 1: Set capacity for 4, 12, and 54 seat vehicles
    def test_01_vehicle_capacities_configured(self):
        self.assertEqual(self.cap_day1_car.total_capacity, 4)
        self.assertEqual(self.cap_day1_micro.total_capacity, 12)
        self.assertEqual(self.cap_day1_bus.total_capacity, 54)
        self.assertEqual(self.cap_day1_car.public_sellable, 4)
        self.assertEqual(self.cap_day1_micro.public_sellable, 12)
        self.assertEqual(self.cap_day1_bus.public_sellable, 54)

    # Test 2: Independent inventory per date/departure
    def test_02_independent_inventory_per_departure(self):
        # Book 4 seats on Day 1 Private Car (selling it out)
        res = BookingService.create_tour_booking(
            customer=self.customer,
            tour=self.tour,
            departure=self.dep_day1,
            vehicle_type=self.vt_car,
            adults=4,
            source="DIRECT"
        )
        self.assertTrue(res['success'])
        self.cap_day1_car.refresh_from_db()
        self.cap_day2_car.refresh_from_db()

        # Day 1 is now sold out (0 sellable)
        self.assertEqual(self.cap_day1_car.public_sellable, 0)
        self.assertFalse(self.cap_day1_car.is_sellable)

        # Day 2 still has full 4 seats available (Independent inventory)
        self.assertEqual(self.cap_day2_car.public_sellable, 4)
        self.assertTrue(self.cap_day2_car.is_sellable)

    # Test 3: Direct + OTA (simulated) bookings deduct from the same inventory
    def test_03_cross_channel_unified_deduction(self):
        # Direct website booking for 2 seats on Micro (12 total)
        res_direct = BookingService.create_tour_booking(
            customer=self.customer,
            tour=self.tour,
            departure=self.dep_day1,
            vehicle_type=self.vt_micro,
            adults=2,
            source="DIRECT"
        )
        self.assertTrue(res_direct['success'])
        self.cap_day1_micro.refresh_from_db()
        self.assertEqual(self.cap_day1_micro.booked_count, 2)
        self.assertEqual(self.cap_day1_micro.public_sellable, 10)

        # Simulated GetYourGuide OTA booking for 4 seats on the exact same Micro departure
        res_gyg = BookingService.create_tour_booking(
            customer=self.customer,
            tour=self.tour,
            departure=self.dep_day1,
            vehicle_type=self.vt_micro,
            adults=4,
            source="GETYOURGUIDE",
            external_reference="GYG-NO-987654"
        )
        self.assertTrue(res_gyg['success'])
        self.cap_day1_micro.refresh_from_db()
        self.assertEqual(self.cap_day1_micro.booked_count, 6)
        self.assertEqual(self.cap_day1_micro.public_sellable, 6)

        # Simulated Viator OTA booking for 3 seats
        res_viator = BookingService.create_tour_booking(
            customer=self.customer,
            tour=self.tour,
            departure=self.dep_day1,
            vehicle_type=self.vt_micro,
            adults=3,
            source="VIATOR",
            external_reference="VIA-882211"
        )
        self.assertTrue(res_viator['success'])
        self.cap_day1_micro.refresh_from_db()
        self.assertEqual(self.cap_day1_micro.booked_count, 9)
        self.assertEqual(self.cap_day1_micro.public_sellable, 3)

    # Test 4: Overbooking protection — final-seat booking does NOT oversell
    def test_04_overbooking_prevention_atomic(self):
        # 3 seats booked out of 4 on Private Car
        BookingService.create_tour_booking(
            customer=self.customer,
            tour=self.tour,
            departure=self.dep_day1,
            vehicle_type=self.vt_car,
            adults=3,
            source="DIRECT"
        )
        self.cap_day1_car.refresh_from_db()
        self.assertEqual(self.cap_day1_car.public_sellable, 1)

        # Attempt to book 2 seats (exceeds 1 remaining) -> Must FAIL
        res_overflow = BookingService.create_tour_booking(
            customer=self.customer,
            tour=self.tour,
            departure=self.dep_day1,
            vehicle_type=self.vt_car,
            adults=2,
            source="DIRECT"
        )
        self.assertFalse(res_overflow['success'])
        self.assertIn("available for Private Car", res_overflow['error'])

        # Verify booked_count did not increase
        self.cap_day1_car.refresh_from_db()
        self.assertEqual(self.cap_day1_car.booked_count, 3)
        self.assertEqual(self.cap_day1_car.public_sellable, 1)

    # Test 5: Sold-out applies only to specific date/time/vehicle
    def test_05_sold_out_isolated_to_vehicle_and_departure(self):
        # Sell out Day 1 Private Car
        BookingService.create_tour_booking(
            customer=self.customer,
            tour=self.tour,
            departure=self.dep_day1,
            vehicle_type=self.vt_car,
            adults=4,
            source="DIRECT"
        )
        self.cap_day1_car.refresh_from_db()
        self.assertEqual(self.cap_day1_car.public_sellable, 0)

        # Day 1 Micro is still available with 12 seats
        self.cap_day1_micro.refresh_from_db()
        self.assertEqual(self.cap_day1_micro.public_sellable, 12)

        # Day 1 Bus is still available with 54 seats
        self.cap_day1_bus.refresh_from_db()
        self.assertEqual(self.cap_day1_bus.public_sellable, 54)

    # Test 6: Cancellation releases capacity
    def test_06_cancellation_releases_capacity(self):
        res = BookingService.create_tour_booking(
            customer=self.customer,
            tour=self.tour,
            departure=self.dep_day1,
            vehicle_type=self.vt_micro,
            adults=5,
            source="DIRECT"
        )
        self.assertTrue(res['success'])
        self.cap_day1_micro.refresh_from_db()
        self.assertEqual(self.cap_day1_micro.booked_count, 5)
        self.assertEqual(self.cap_day1_micro.public_sellable, 7)

        # Cancel booking
        booking = Booking.objects.get(id=res['booking_id'])
        trans_res = BookingService.transition_status(booking, "CANCELLED", reason="Customer request")
        self.assertTrue(trans_res)

        # Capacity must be immediately restored
        self.cap_day1_micro.refresh_from_db()
        self.assertEqual(self.cap_day1_micro.booked_count, 0)
        self.assertEqual(self.cap_day1_micro.public_sellable, 12)

    # Test 7: Expiry of held bookings releases seats
    def test_07_held_booking_expiry(self):
        res = BookingService.create_held_booking(
            customer=self.customer,
            tour=self.tour,
            departure=self.dep_day1,
            vehicle_type=self.vt_micro,
            adults=4,
            hold_minutes=15
        )
        self.assertTrue(res['success'])
        self.cap_day1_micro.refresh_from_db()
        self.assertEqual(self.cap_day1_micro.booked_count, 4)

        # Artificially age the hold
        booking = Booking.objects.get(id=res['booking_id'])
        booking.hold_expires_at = timezone.now() - datetime.timedelta(minutes=1)
        booking.save(update_fields=['hold_expires_at'])

        # Run expiry job
        expired_count = BookingService.expire_held_bookings()
        self.assertEqual(expired_count, 1)

        booking.refresh_from_db()
        self.assertEqual(booking.status, "EXPIRED")

        # Capacity must be returned
        self.cap_day1_micro.refresh_from_db()
        self.assertEqual(self.cap_day1_micro.booked_count, 0)
        self.assertEqual(self.cap_day1_micro.public_sellable, 12)

    # Test 8: Manual booking from phone/concierge
    def test_08_manual_admin_booking(self):
        res = BookingService.create_tour_booking(
            customer=self.customer,
            tour=self.tour,
            departure=self.dep_day1,
            vehicle_type=self.vt_bus,
            adults=15,
            source="MANUAL",
            external_reference="HOTEL-RADISSON-CONCIERGE"
        )
        self.assertTrue(res['success'])
        self.cap_day1_bus.refresh_from_db()
        self.assertEqual(self.cap_day1_bus.booked_count, 15)
        self.assertEqual(self.cap_day1_bus.public_sellable, 39)

    # Test 9: Next-day departure block/close
    def test_09_departure_block_close(self):
        client = Client()
        client.force_login(self.admin_user)

        # Toggle Day 2 status to BLOCKED via API
        url = reverse('departure_status_api', args=[self.dep_day2.id])
        resp = client.post(url, data='{"status": "BLOCKED"}', content_type='application/json')
        self.assertEqual(resp.status_code, 200)

        self.dep_day2.refresh_from_db()
        self.assertEqual(self.dep_day2.status, "BLOCKED")

        # Attempt to book on blocked departure -> Must FAIL
        res = BookingService.create_tour_booking(
            customer=self.customer,
            tour=self.tour,
            departure=self.dep_day2,
            vehicle_type=self.vt_car,
            adults=2,
            source="DIRECT"
        )
        self.assertFalse(res['success'])
        self.assertIn("blocked", res['error'].lower())

    # Test 10: Guaranteed re-attempt guest moved to next day -> capacity adjusts
    def test_10_guaranteed_reattempt_and_rebooking(self):
        # Customer booked Day 1 Micro
        res = BookingService.create_tour_booking(
            customer=self.customer,
            tour=self.tour,
            departure=self.dep_day1,
            vehicle_type=self.vt_micro,
            adults=3,
            source="DIRECT"
        )
        booking = Booking.objects.get(id=res['booking_id'])
        tour_booking = booking.tour_booking

        # Experience fails (no aurora visible), trigger Guaranteed Re-attempt
        reattempt = GuaranteedReattempt.objects.create(
            original_booking=booking,
            original_departure=self.dep_day1,
            reattempt_departure=self.dep_day2,
            guests_count=3,
            reason="WEATHER",
            status="ELIGIBLE"
        )
        # Reserve re-attempt seats on Day 2 departure
        DepartureService.reserve_reattempt_seats(self.cap_day2_micro.id, 3)

        # Verify Day 2 sellable capacity is reduced by 3 (reattempt_reserved=3)
        self.cap_day2_micro.refresh_from_db()
        self.assertEqual(self.cap_day2_micro.reattempt_reserved, 3)
        self.assertEqual(self.cap_day2_micro.public_sellable, 9)  # 12 - 0 - 0 - 3 = 9

        # Now rebook guest from Day 1 to Day 2
        rebook_res = BookingService.rebook_departure(
            booking=booking,
            new_departure=self.dep_day2,
            new_vehicle_type=self.vt_micro
        )
        self.assertTrue(rebook_res['success'])

        # Resolve reattempt
        reattempt.status = "REBOOKED"
        reattempt.reattempt_booking = booking
        reattempt.save()
        DepartureService.release_reattempt_seats(self.cap_day2_micro.id, 3)

        # Verify Day 1 capacity is released (0 booked)
        self.cap_day1_micro.refresh_from_db()
        self.assertEqual(self.cap_day1_micro.booked_count, 0)
        self.assertEqual(self.cap_day1_micro.public_sellable, 12)

        # Verify Day 2 has 3 booked seats and 0 reattempt_reserved (9 sellable)
        self.cap_day2_micro.refresh_from_db()
        self.assertEqual(self.cap_day2_micro.booked_count, 3)
        self.assertEqual(self.cap_day2_micro.reattempt_reserved, 0)
        self.assertEqual(self.cap_day2_micro.public_sellable, 9)

    # Test 11: Blocked seats excluded from public sellable capacity
    def test_11_blocked_seats_excluded(self):
        # Admin blocks 4 seats for maintenance / driver VIP on Group Bus
        self.cap_day1_bus.blocked_seats = 4
        self.cap_day1_bus.save()

        self.assertEqual(self.cap_day1_bus.public_sellable, 50)  # 54 - 4 = 50

        # Customer attempts to book 51 seats -> Must FAIL
        res = BookingService.create_tour_booking(
            customer=self.customer,
            tour=self.tour,
            departure=self.dep_day1,
            vehicle_type=self.vt_bus,
            adults=51,
            source="DIRECT"
        )
        self.assertFalse(res['success'])

    # Test 12: OTA sync failure logging & admin notification
    def test_12_sync_failure_logged_and_alerted(self):
        channel, _ = Channel.objects.get_or_create(
            slug="viator",
            defaults={"name": "Viator", "adapter_class": "channels.adapters.viator.ViatorAdapter", "is_active": True}
        )

        # Simulate a failed sync event
        log = ChannelSyncLog.objects.create(
            channel=channel,
            departure=self.dep_day1,
            action="AVAILABILITY_PUSH",
            status="FAILED",
            error_message="HTTP 503 Service Unavailable from Viator API endpoint",
            retry_count=1,
            requires_attention=True
        )

        # Verify it requires attention
        self.assertTrue(log.requires_attention)
        failed_count = ChannelSyncLog.objects.filter(status="FAILED").count()
        self.assertGreaterEqual(failed_count, 1)

        # Test context processor injects the warning into the admin notification bell
        client = Client()
        client.force_login(self.admin_user)
        resp = client.get('/admin/operations/calendar/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('admin_notifications', resp.context)
        self.assertTrue(any('OTA Channel Sync Failure' in n['title'] for n in resp.context['admin_notifications']))
        self.assertGreaterEqual(resp.context['admin_unread_count'], 1)
