from decimal import Decimal
from django.db import models
from django.conf import settings
# --- TAXONOMY MODELS ---

class Country(models.Model):
    name = models.CharField(max_length=150) # e.g. Finland
    slug = models.SlugField(unique=True)
    subtitle = models.CharField(max_length=250, blank=True, help_text="Short card tagline")
    description = models.TextField(blank=True)
    region = models.CharField(max_length=100, default='Popular', blank=True, help_text="Filter tab e.g. Popular, Northern Europe, Scandinavia")
    hero_image = models.ImageField(upload_to='countries/', blank=True, null=True)
    flag_icon = models.ImageField(upload_to='countries/flags/', blank=True, null=True, help_text="Upload flag or icon for mega menu sidebar")
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured_in_nav = models.BooleanField(default=True, help_text="Show in Destination Mega Menu sidebar")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

    @property
    def get_flag_url(self):
        if self.flag_icon:
            return self.flag_icon.url
        slug_str = f"{self.slug} {self.name}".lower()
        if 'denmark' in slug_str:
            return '/media/countries/flags/flag_denmark.svg'
        if 'sweden' in slug_str:
            return '/media/countries/flags/flag_sweden.svg'
        if 'norway' in slug_str:
            return '/media/countries/flags/flag_norway.svg'
        if 'iceland' in slug_str:
            return '/media/countries/flags/flag_iceland.svg'
        return '/media/countries/flags/flag_finland.svg'

class Destination(models.Model):
    name = models.CharField(max_length=150) # e.g. Rovaniemi
    slug = models.SlugField(unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='destinations', null=True, blank=True)
    description = models.TextField(blank=True)
    highlights = models.TextField(blank=True, help_text="Key highlights / attractions (e.g. Santa Claus Village, Arktikum)")
    hero_image = models.ImageField(upload_to='destinations/', blank=True, null=True)
    nav_icon = models.ImageField(upload_to='destinations/nav_icons/', blank=True, null=True, help_text="Upload circular icon/image for navigation mega menu")
    hero_image_alt = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured_in_nav = models.BooleanField(default=True, help_text="Show in Destination Mega Menu circular grid")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        if self.country:
            return f"{self.name} ({self.country.name})"
        return self.name

    @property
    def get_flag_url(self):
        if self.country and self.country.flag_icon:
            return self.country.flag_icon.url
        slug_str = f"{self.slug} {self.name} {self.country.slug if self.country else ''}".lower()
        if 'denmark' in slug_str or 'copenhagen' in slug_str:
            return '/media/countries/flags/flag_denmark.svg'
        if 'sweden' in slug_str or 'stockholm' in slug_str or 'kiruna' in slug_str or 'abisko' in slug_str:
            return '/media/countries/flags/flag_sweden.svg'
        if 'norway' in slug_str or 'oslo' in slug_str or 'troms' in slug_str:
            return '/media/countries/flags/flag_norway.svg'
        if 'iceland' in slug_str or 'reykjavik' in slug_str:
            return '/media/countries/flags/flag_iceland.svg'
        return '/media/countries/flags/flag_finland.svg'

class Season(models.Model):
    name = models.CharField(max_length=50) # e.g. Winter, Summer
    slug = models.SlugField(unique=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class ExperienceType(models.Model):
    name = models.CharField(max_length=100) # e.g. Northern Lights, Adventure
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=100, blank=True, help_text="CSS icon class")
    image = models.ImageField(upload_to='experiences/', blank=True, null=True, help_text="Circular thumbnail for Tour Mega Menu")
    nav_icon = models.ImageField(upload_to='experiences/nav_icons/', blank=True, null=True, help_text="Upload circular icon image for Tour Mega Menu")
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)
    is_featured_in_nav = models.BooleanField(default=True, help_text="Show in Tour Mega Menu circular grid")

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name

class TravelStyle(models.Model):
    name = models.CharField(max_length=100) # e.g. Private, Small Group
    slug = models.SlugField(unique=True)
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class DurationBand(models.Model):
    name = models.CharField(max_length=100) # e.g. Half Day, 2-3 Days
    slug = models.SlugField(unique=True)
    min_hours = models.IntegerField()
    max_hours = models.IntegerField()
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name


# --- VEHICLE TYPE (Global Tour Transport Categories) ---

class VehicleType(models.Model):
    """
    System-level vehicle categories for tour departures.
    Pre-seeded: Private Car (4), Micro (12), Group Bus (54).
    Admin can add future types without code changes.
    """
    name = models.CharField(max_length=100)  # e.g. "Private Car"
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji or CSS icon class, e.g. 🚗")
    default_capacity = models.PositiveIntegerField(help_text="Default seat count for this vehicle type")
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order', 'default_capacity']
        verbose_name = "Vehicle Type"
        verbose_name_plural = "Vehicle Types"

    def __str__(self):
        return f"{self.name} ({self.default_capacity} seats)"


# --- TOUR PRODUCT MODELS ---

class Tour(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True)
    short_summary = models.TextField(help_text="Card description, max 200 chars")
    overview = models.TextField(help_text="Rich text - full description")
    
    destination = models.ForeignKey(Destination, on_delete=models.RESTRICT, related_name='tours')
    travel_style = models.ForeignKey(TravelStyle, on_delete=models.RESTRICT, related_name='tours')
    duration_band = models.ForeignKey(DurationBand, on_delete=models.RESTRICT, related_name='tours')
    seasons = models.ManyToManyField(Season, related_name='tours')
    experience_types = models.ManyToManyField(ExperienceType, related_name='tours')
    
    duration_text = models.CharField(max_length=100) # e.g. 3 Days / 2 Nights
    meeting_point = models.CharField(max_length=250, blank=True, null=True)
    transportation_info = models.TextField(blank=True, null=True)
    accommodation_info = models.TextField(blank=True, null=True)
    meal_info = models.TextField(blank=True, null=True)
    event_ticket_info = models.TextField(blank=True, null=True)
    cancellation_terms = models.TextField()
    
    STATUS_CHOICES = (('DRAFT', 'Draft'), ('PUBLISHED', 'Published'), ('ARCHIVED', 'Archived'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    is_featured = models.BooleanField(default=False)
    badge_text = models.CharField(max_length=50, blank=True, help_text="Marketing badge ribbon e.g. 'Best Seller', '15% Off', 'Top Rated'")
    is_group_tour = models.BooleanField(default=True, verbose_name="Group Tour", help_text="Show in 'Group tours' category on homepage")
    is_private_tour = models.BooleanField(default=False, verbose_name="Private Tour", help_text="Show in 'Private tours' category on homepage")
    is_family_tour = models.BooleanField(default=False, verbose_name="Family Tour", help_text="Show in 'Family tours' category on homepage")
    sort_order = models.IntegerField(default=0)
    has_guaranteed_reattempt = models.BooleanField(
        default=False,
        help_text="Enable guaranteed re-attempt policy (e.g., Northern Lights). "
                  "Failed experiences allow customers to re-attempt on the next available day."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def category_tags(self):
        tags = []
        if self.is_group_tour:
            tags.append('group')
        if self.is_private_tour:
            tags.append('private')
        if self.is_family_tour:
            tags.append('family')
        if not tags:
            style_name = (self.travel_style.name if self.travel_style else '').lower()
            if 'family' in style_name:
                tags.append('family')
            elif any(k in style_name for k in ['private', 'vip', 'luxury']):
                tags.append('private')
            else:
                tags.append('group')
        return ' '.join(tags)

    @property
    def base_price(self):
        adult_pricing = self.pricing.filter(label__iexact='Adult').first()
        if adult_pricing:
            return adult_pricing.price
        first_pricing = self.pricing.first()
        if first_pricing:
            return first_pricing.price
        return Decimal('100.00')

    def __str__(self):
        return self.title

class TourMedia(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='tours/media/')
    alt_text = models.CharField(max_length=200, blank=True)
    MEDIA_TYPES = (('IMAGE', 'Image'), ('VIDEO', 'Video'))
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default='IMAGE')
    is_hero = models.BooleanField(default=False, help_text="Only one per tour")
    sort_order = models.IntegerField(default=0)

class TourHighlight(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='highlights')
    text = models.CharField(max_length=200)
    icon = models.CharField(max_length=100, blank=True)
    sort_order = models.IntegerField(default=0)

class TourItinerary(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='itinerary')
    day_number = models.IntegerField()
    title = models.CharField(max_length=200) # e.g. Day 1: Arrival
    description = models.TextField()
    image = models.ImageField(upload_to='tours/itineraries/', blank=True, null=True, help_text="Optional photo for this itinerary day")
    sort_order = models.IntegerField(default=0)

class TourExtraService(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='extra_services')
    name = models.CharField(max_length=150) # e.g. "Thermal Snowsuit Rental"
    price = models.DecimalField(max_digits=10, decimal_places=2)
    PRICE_TYPE_CHOICES = (
        ('PER_PERSON', 'Per Person'),
        ('PER_BOOKING', 'Per Booking (Flat)'),
    )
    price_type = models.CharField(max_length=20, choices=PRICE_TYPE_CHOICES, default='PER_PERSON')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.name} (+€{self.price} {self.get_price_type_display()})"

class TourInclusion(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='inclusions')
    text = models.CharField(max_length=200)
    is_included = models.BooleanField(default=True, help_text="True=Included, False=Excluded")
    sort_order = models.IntegerField(default=0)

class TourFAQ(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=250)
    answer = models.TextField()
    sort_order = models.IntegerField(default=0)

class TourPickup(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='pickups')
    location_name = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_time = models.TimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    TYPE_CHOICES = (('PICKUP', 'Pickup'), ('DROPOFF', 'Dropoff'))
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='PICKUP')

class TourDate(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='dates')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    total_capacity = models.IntegerField()
    booked_count = models.IntegerField(default=0)
    STATUS_CHOICES = (('AVAILABLE', 'Available'), ('SOLD_OUT', 'Sold Out'), ('CANCELLED', 'Cancelled'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def available_spots(self):
        return max(0, self.total_capacity - self.booked_count)

    def __str__(self):
        return f"{self.tour.title} ({self.start_date})"

class TourPricing(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='pricing')
    label = models.CharField(max_length=100) # e.g. Adult, Child
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    min_quantity = models.IntegerField(default=1)
    max_quantity = models.IntegerField(null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name='pricing')
    early_bird_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    early_bird_deadline = models.DateField(null=True, blank=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class TourReview(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField() # 1-5
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class RelatedTour(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='related_tours')
    related_tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    sort_order = models.IntegerField(default=0)

class TourCategory(models.Model):
    name = models.CharField(max_length=150) # e.g. Day Tours, Multi-Day Tours, Private Tours
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='tour_categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Tour Categories"

    def __str__(self):
        return self.name

class TourSurrounding(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='surroundings')
    name = models.CharField(max_length=200) # e.g. "Hotel Kämp", "Helsinki Cathedral"
    distance_text = models.CharField(max_length=100) # e.g. "500m", "2 km"
    TYPE_CHOICES = (
        ('RESTAURANT', 'Restaurant'), ('HOTEL', 'Hotel'), ('LANDMARK', 'Landmark'),
        ('TRANSPORT', 'Transport'), ('SHOPPING', 'Shopping'), ('OTHER', 'Other')
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='LANDMARK')
    sort_order = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.distance_text})"

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'tour') # A user can only wishlist a tour once

    def __str__(self):
        return f"{self.user.email} → {self.tour.title}"


# --- DEPARTURE & CAPACITY MODELS (OTA Central Booking Architecture) ---

class TourOptionPricing(models.Model):
    """
    Per-tour, per-vehicle-type pricing.
    E.g. 'Northern Lights Hunt' via Private Car = €299/adult, €149/child.
    Every tour has pricing for each active VehicleType.
    """
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='option_pricing')
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, related_name='tour_pricing')

    adult_price = models.DecimalField(max_digits=10, decimal_places=2)
    child_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')

    early_bird_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    early_bird_child_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    early_bird_deadline = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('tour', 'vehicle_type')
        verbose_name = "Tour Option Pricing"
        verbose_name_plural = "Tour Option Pricing"

    def __str__(self):
        return f"{self.tour.title} — {self.vehicle_type.name} (€{self.adult_price}/adult)"


class Departure(models.Model):
    """
    A specific bookable date+time slot when a tour runs.
    Each departure has independent capacity per vehicle type via DepartureCapacity.
    """
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='departures')
    date = models.DateField()
    time = models.TimeField()

    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
        ('SOLD_OUT', 'Sold Out'),
        ('BLOCKED', 'Blocked'),
        ('OPERATIONALLY_RESERVED', 'Operationally Reserved'),
    )
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='OPEN')
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'time']
        unique_together = ('tour', 'date', 'time')
        verbose_name = "Departure"
        verbose_name_plural = "Departures"

    def __str__(self):
        return f"{self.tour.title} — {self.date} @ {self.time.strftime('%H:%M')}"


class DepartureCapacity(models.Model):
    """
    Per-departure, per-vehicle-type independent inventory.
    All channels (Direct, OTA, Manual) deduct from the same record.
    
    Capacity formula:
        Public Sellable = total_capacity - booked_count - blocked_seats - reattempt_reserved
    """
    departure = models.ForeignKey(Departure, on_delete=models.CASCADE, related_name='capacities')
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, related_name='departure_capacities')

    total_capacity = models.PositiveIntegerField(help_text="Total seats for this vehicle type on this departure")
    booked_count = models.PositiveIntegerField(default=0, help_text="Seats confirmed or held across all channels")
    blocked_seats = models.PositiveIntegerField(default=0, help_text="Admin-blocked seats (not for sale)")
    reattempt_reserved = models.PositiveIntegerField(default=0, help_text="Seats reserved for guaranteed re-attempt guests")

    # Optional per-departure price override (if null, uses TourOptionPricing)
    price_override_adult = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Override adult price for this specific departure. Leave blank to use tour option pricing.")
    price_override_child = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Override child price for this specific departure. Leave blank to use tour option pricing.")

    class Meta:
        unique_together = ('departure', 'vehicle_type')
        verbose_name = "Departure Capacity"
        verbose_name_plural = "Departure Capacities"

    @property
    def public_sellable(self):
        """What the website and OTAs can sell."""
        return max(0, self.total_capacity - self.booked_count - self.blocked_seats - self.reattempt_reserved)

    @property
    def is_sold_out(self):
        return self.public_sellable <= 0

    @property
    def is_sellable(self):
        return self.public_sellable > 0

    def __str__(self):
        return f"{self.departure} — {self.vehicle_type.name}: {self.public_sellable}/{self.total_capacity} available"
