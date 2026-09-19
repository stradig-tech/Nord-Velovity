from decimal import Decimal
from django.db import models

class VehicleClass(models.Model):
    name = models.CharField(max_length=100) # e.g. Business, First Class, VIP
    slug = models.SlugField(unique=True)
    description = models.TextField()
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    vehicle_class = models.ForeignKey(VehicleClass, on_delete=models.CASCADE, related_name='vehicles')
    name = models.CharField(max_length=100) # e.g. Mercedes S-Class
    passenger_capacity = models.IntegerField()
    luggage_capacity = models.IntegerField()
    features = models.JSONField(default=dict, blank=True, help_text="Features list or JSON (e.g. Wi-Fi, Heated Seats)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def features_list(self):
        """Returns features as a clean list of string labels regardless of storage format (dict, list, string)."""
        if isinstance(self.features, list):
            return [str(item).strip() for item in self.features if str(item).strip()]
        if isinstance(self.features, dict):
            items = []
            for k, v in self.features.items():
                if v is True or v == "true" or v == 1:
                    items.append(k.replace('_', ' ').title())
                elif v:
                    items.append(f"{k.replace('_', ' ').title()}: {v}")
            return items
        if isinstance(self.features, str):
            return [f.strip() for f in self.features.replace('\n', ',').split(',') if f.strip()]
        return []

    def clean(self):
        super().clean()
        if isinstance(self.features, str):
            data = self.features.strip()
            if not data:
                self.features = []
            else:
                try:
                    import json
                    self.features = json.loads(data)
                except Exception:
                    self.features = [item.strip() for item in data.replace('\n', ',').split(',') if item.strip()]

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.vehicle_class.name})"

class PricingRule(models.Model):
    vehicle_class = models.ForeignKey(VehicleClass, on_delete=models.CASCADE, related_name='pricing_rules')
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    per_km_rate = models.DecimalField(max_digits=10, decimal_places=2)
    per_minute_rate = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_fare = models.DecimalField(max_digits=10, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pricing for {self.vehicle_class.name}"


class VehiclePhoto(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    vehicle_class = models.ForeignKey(VehicleClass, on_delete=models.CASCADE, related_name='photos', null=True, blank=True)
    image_file = models.ImageField(upload_to='vehicles/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = "Cab Photo"
        verbose_name_plural = "Cab Photos"

    def __str__(self):
        target = self.vehicle.name if self.vehicle else (self.vehicle_class.name if self.vehicle_class else "Fleet")
        return f"Photo for {target}"

class FixedRoute(models.Model):
    """
    Fixed Price Transfer — predefined fixed-price transfers between any two locations.
    Supports airports, cities, hotels, resorts, attractions, and custom routes.
    Airport is one possible transfer type, not a requirement.
    """
    name = models.CharField(max_length=200, help_text="e.g. Helsinki Airport → City Center, Levi Resort → Kittilä Airport")
    slug = models.SlugField(unique=True)

    TRANSFER_TYPE_CHOICES = (
        ('AIRPORT', 'Airport Transfer'),
        ('CITY', 'City-to-City Transfer'),
        ('HOTEL', 'Hotel Transfer'),
        ('RESORT', 'Resort Transfer'),
        ('ATTRACTION', 'Attraction Transfer'),
        ('CUSTOM', 'Custom Transfer'),
    )
    transfer_type = models.CharField(
        max_length=20, choices=TRANSFER_TYPE_CHOICES, default='AIRPORT',
        help_text="Category of this fixed price transfer"
    )

    # Generic origin/destination (pickup → drop-off)
    pickup_name = models.CharField(max_length=200, help_text="Pickup location name, e.g. Helsinki-Vantaa Airport, Hotel Kämp, Santa Claus Village")
    pickup_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, default=Decimal('0.000000'), help_text="Optional latitude (defaults to 0.0 if not geocoded)")
    pickup_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, default=Decimal('0.000000'), help_text="Optional longitude (defaults to 0.0 if not geocoded)")
    dropoff_name = models.CharField(max_length=200, help_text="Drop-off location name")
    dropoff_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, default=Decimal('0.000000'), help_text="Optional latitude (defaults to 0.0 if not geocoded)")
    dropoff_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, default=Decimal('0.000000'), help_text="Optional longitude (defaults to 0.0 if not geocoded)")

    distance_km = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default=Decimal('10.00'), help_text="Distance in km (defaults to 10.0 if not calculated)")
    estimated_duration_min = models.IntegerField(null=True, blank=True, default=20, help_text="Duration in minutes (defaults to 20 if not calculated)")

    vehicle_class = models.ForeignKey(VehicleClass, on_delete=models.CASCADE, related_name='fixed_routes')
    fixed_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR', blank=True)

    # Capacity
    passenger_capacity = models.PositiveIntegerField(default=4, blank=True, help_text="Max passengers for this transfer route")
    luggage_capacity = models.PositiveIntegerField(default=2, blank=True, help_text="Max luggage pieces for this transfer route")

    is_return_available = models.BooleanField(default=False)
    return_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    description = models.TextField(blank=True, help_text="Customer-facing description of this transfer route")
    notes = models.TextField(blank=True, help_text="Internal admin notes")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['transfer_type', 'name']
        verbose_name = "Fixed Price Transfer"
        verbose_name_plural = "Fixed Price Transfers"

    def clean(self):
        super().clean()
        if not self.currency:
            self.currency = 'EUR'
        if not self.passenger_capacity:
            self.passenger_capacity = 4
        if not self.luggage_capacity:
            self.luggage_capacity = 2

    def save(self, *args, **kwargs):
        self.clean()
        if self.pickup_lat is None:
            self.pickup_lat = Decimal('0.000000')
        if self.pickup_lng is None:
            self.pickup_lng = Decimal('0.000000')
        if self.dropoff_lat is None:
            self.dropoff_lat = Decimal('0.000000')
        if self.dropoff_lng is None:
            self.dropoff_lng = Decimal('0.000000')
        if self.distance_km is None:
            self.distance_km = Decimal('10.00')
        if self.estimated_duration_min is None:
            self.estimated_duration_min = 20
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pickup_name} -> {self.dropoff_name} ({self.vehicle_class.name})"

class Zone(models.Model):
    name = models.CharField(max_length=150) # e.g. Helsinki City Center
    boundary_polygon = models.JSONField(help_text="GeoJSON coordinates")
    surcharge_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    SURCHARGE_CHOICES = (('FLAT', 'Flat Fee'), ('PERCENT', 'Percentage'))
    surcharge_type = models.CharField(max_length=10, choices=SURCHARGE_CHOICES, default='FLAT')
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Surcharge(models.Model):
    name = models.CharField(max_length=150) # e.g. Night Surcharge
    
    CATEGORY_CHOICES = (
        ('NIGHT', 'Night'), ('WEEKEND', 'Weekend'), 
        ('HOLIDAY', 'Holiday'), ('PEAK', 'Peak Hour'), ('CUSTOM', 'Custom')
    )
    surcharge_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    AMOUNT_CHOICES = (('FLAT', 'Flat Fee'), ('PERCENT', 'Percentage'))
    amount_type = models.CharField(max_length=10, choices=AMOUNT_CHOICES)
    
    start_time = models.TimeField(null=True, blank=True) # e.g. 22:00
    end_time = models.TimeField(null=True, blank=True) # e.g. 06:00
    applicable_days = models.JSONField(default=list, help_text="[5, 6] for Sat/Sun")
    specific_date = models.DateField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AvailabilityRule(models.Model):
    vehicle_class = models.ForeignKey(VehicleClass, on_delete=models.CASCADE, related_name='availability_rules')
    zone = models.ForeignKey(Zone, on_delete=models.SET_NULL, null=True, blank=True, related_name='availability_rules')
    
    day_of_week = models.IntegerField(help_text="0=Mon, 6=Sun")
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rule for {self.vehicle_class.name} on day {self.day_of_week}"


class ChauffeurServiceStandard(models.Model):
    vehicle_class = models.ForeignKey(
        VehicleClass, 
        on_delete=models.CASCADE, 
        related_name='service_standards',
        null=True, 
        blank=True,
        help_text="Applies to a specific vehicle class. Leave blank to apply globally to all classes."
    )
    title = models.CharField(max_length=300, help_text="Standard policy or service guarantee")
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = "Chauffeur Service Standard"
        verbose_name_plural = "Chauffeur Service Standards"

    def __str__(self):
        prefix = f"[{self.vehicle_class.name}] " if self.vehicle_class else "[Global] "
        return f"{prefix}{self.title}"


class ChauffeurInclusion(models.Model):
    vehicle_class = models.ForeignKey(
        VehicleClass, 
        on_delete=models.CASCADE, 
        related_name='inclusions',
        null=True, 
        blank=True,
        help_text="Applies to a specific vehicle class. Leave blank to apply globally to all classes."
    )
    text = models.CharField(max_length=255)
    is_included = models.BooleanField(
        default=True, 
        help_text="True = Included in your price, False = Extra charge"
    )
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = "Chauffeur Inclusion / Exclusion"
        verbose_name_plural = "Chauffeur Inclusions & Exclusions"

    def __str__(self):
        status = "Included" if self.is_included else "Extra Charge"
        prefix = f"[{self.vehicle_class.name}] " if self.vehicle_class else "[Global] "
        return f"{prefix}{self.text} ({status})"


class ChauffeurSafetyStandard(models.Model):
    vehicle_class = models.ForeignKey(
        VehicleClass, 
        on_delete=models.CASCADE, 
        related_name='safety_standards',
        null=True, 
        blank=True,
        help_text="Applies to a specific vehicle class. Leave blank to apply globally to all classes."
    )
    text = models.CharField(max_length=300)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = "Safety & Luxury Standard"
        verbose_name_plural = "Safety & Luxury Standards"

    def __str__(self):
        prefix = f"[{self.vehicle_class.name}] " if self.vehicle_class else "[Global] "
        return f"{prefix}{self.text}"

