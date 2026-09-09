from django.core.management.base import BaseCommand
from bookings.services import BookingService


class Command(BaseCommand):
    help = "Expire unconfirmed held bookings past their hold expiration timeout and release seats back to inventory."

    def handle(self, *args, **options):
        expired_count = BookingService.expire_held_bookings()
        if expired_count > 0:
            self.stdout.write(self.style.SUCCESS(f"Successfully expired {expired_count} held booking(s) and restored capacity."))
        else:
            self.stdout.write(self.style.SUCCESS("No held bookings needed expiration."))
