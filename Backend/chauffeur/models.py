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
    features = models.JSONField(default=dict) # e.g. {"wifi": True, "water": True}
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
    name = models.CharField(max_length=150) # e.g. Helsinki Airport Transfer
    slug = models.SlugField(unique=True)
    origin_name = models.CharField(max_length=200)
    origin_lat = models.DecimalField(max_digits=9, decimal_places=6)
    origin_lng = models.DecimalField(max_digits=9, decimal_places=6)
    destination_name = models.CharField(max_length=200)
    destination_lat = models.DecimalField(max_digits=9, decimal_places=6)
    destination_lng = models.DecimalField(max_digits=9, decimal_places=6)
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    estimated_duration_min = models.IntegerField()
    
    vehicle_class = models.ForeignKey(VehicleClass, on_delete=models.CASCADE, related_name='fixed_routes')
    fixed_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    
    is_return_available = models.BooleanField(default=False)
    return_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.vehicle_class.name}"

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

