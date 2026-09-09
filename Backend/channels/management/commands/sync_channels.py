from django.core.management.base import BaseCommand
from channels.models import Channel
from channels.services import ChannelSyncService
from tours.models import Departure


class Command(BaseCommand):
    help = "Pushes upcoming departure availability to active OTA channels and retries failed syncs."

    def add_arguments(self, parser):
        parser.add_argument('--retry-failed', action='store_true', help='Only retry failed syncs requiring attention')

    def handle(self, *args, **options):
        if options.get('retry_failed'):
            count = ChannelSyncService.retry_failed_syncs()
            self.stdout.write(self.style.SUCCESS(f"Retried {count} failed sync(s)."))
            return

        active_channels = Channel.objects.filter(is_active=True)
        if not active_channels.exists():
            self.stdout.write("No active OTA channels configured.")
            return

        departures = Departure.objects.filter(status='OPEN')
        synced_count = 0
        for dep in departures:
            ChannelSyncService.push_departure_availability(dep)
            synced_count += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully synced {synced_count} departure(s) across {active_channels.count()} active channel(s)."))
