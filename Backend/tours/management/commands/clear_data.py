from django.core.management.base import BaseCommand
from tours.models import Country, Destination, Season, ExperienceType, TravelStyle, DurationBand, Tour
from chauffeur.models import VehicleClass, Vehicle, PricingRule, FixedRoute, Surcharge
from bookings.models import Booking

class Command(BaseCommand):
    help = 'Clears all test data from the database (keeps Users/Superusers intact)'

    def handle(self, *args, **kwargs):
        self.stdout.write('🗑️ Clearing test data...')
        
        Booking.objects.all().delete()
        
        Tour.objects.all().delete()
        Destination.objects.all().delete()
        Country.objects.all().delete()
        Season.objects.all().delete()
        ExperienceType.objects.all().delete()
        TravelStyle.objects.all().delete()
        DurationBand.objects.all().delete()
        
        Vehicle.objects.all().delete()
        VehicleClass.objects.all().delete()
        PricingRule.objects.all().delete()
        FixedRoute.objects.all().delete()
        Surcharge.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('✅ All test data cleared successfully! (Your admin account is safe)'))
