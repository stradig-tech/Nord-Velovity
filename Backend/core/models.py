from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    ACTION_CHOICES = (('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete'))
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField()
    object_repr = models.CharField(max_length=250)
    changes = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class SiteSetting(models.Model):
    site_name = models.CharField(max_length=150, default="Nord Velocity", blank=True)
    logo = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Main brand & navbar logo")
    favicon = models.ImageField(upload_to='site/', blank=True, null=True, help_text="Browser tab favicon (.ico, .png, .svg)")
    preview_image = models.ImageField(upload_to='site/og/', blank=True, null=True, verbose_name="OG Image (Social Share)", help_text="Upload OpenGraph (OG) image for social media share previews. Default is blank if not uploaded.")
    tagline = models.CharField(max_length=250, default="Exclusive Nordic Tours & Luxury Chauffeur Services", blank=True)
    
    # Homepage Hero Section (All optional)
    hero_title = models.CharField(max_length=250, blank=True, default="Discover the Untamed Beauty of the Nordics", help_text="Main heading in homepage hero banner (optional)")
    hero_subtitle = models.TextField(blank=True, default="Curated Arctic expeditions, glass igloo stays, and VIP chauffeur transfers across Finland and Scandinavia.", help_text="Supporting description below hero title (optional)")
    hero_video_url = models.CharField(max_length=500, blank=True, default="", help_text="Direct video URL (.mp4) (optional)")
    hero_video_file = models.FileField(upload_to='site/videos/', blank=True, null=True, help_text="Optional: Upload local MP4 background video (bypasses YouTube player entirely)")
    hero_background_image = models.ImageField(upload_to='site/hero/', blank=True, null=True, help_text="Optional: High-resolution hero fallback background image")
    
    default_currency = models.CharField(max_length=3, default="EUR", blank=True)
    currency_symbol = models.CharField(max_length=5, default="€", blank=True)
    
    contact_email = models.EmailField(default="concierge@nordvelocity.com", blank=True)
    contact_phone = models.CharField(max_length=50, default="+358 9 1234 567", blank=True)
    emergency_phone = models.CharField(max_length=50, default="+358 40 987 6543", blank=True)
    office_address = models.CharField(max_length=250, default="Pohjoisesplanadi 33, 00100 Helsinki, Finland", blank=True)
    operating_hours = models.CharField(max_length=150, default="Mon - Sun: 08:00 - 22:00 EET", blank=True)
    
    facebook_url = models.URLField(blank=True, default="https://facebook.com/nordvelocity")
    instagram_url = models.URLField(blank=True, default="https://instagram.com/nordvelocity")
    linkedin_url = models.URLField(blank=True, default="https://linkedin.com/company/nordvelocity")
    tripadvisor_url = models.URLField(blank=True, default="https://tripadvisor.com")
    social_links = models.JSONField(default=dict, blank=True)
    
    footer_text = models.TextField(default="Nord Velocity is Scandinavia's premier luxury travel designer, providing bespoke Arctic tours, private husky expeditions, and VIP chauffeur services.", blank=True)
    copyright_text = models.CharField(max_length=200, default="© 2026 Nord Velocity Oy. All rights reserved.", blank=True)
    
    google_maps_embed_url = models.TextField(blank=True, default="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d1984.7!2d24.945!3d60.168!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zNjDCsDEwJzA0LjgiTiAyNMKwNTYnNDIuMCJF!5e0!3m2!1sen!2sfi!4v1600000000000!5m2!1sen!2sfi")
    
    # Offline & Bank Wire Transfer Settings
    bank_name = models.CharField(max_length=150, default="Nordea Bank Finland", blank=True)
    bank_account_name = models.CharField(max_length=150, default="Nord Velocity Oy", blank=True)
    bank_iban = models.CharField(max_length=50, default="FI12 3456 7890 1234 56", blank=True)
    bank_swift_bic = models.CharField(max_length=20, default="NDEAFIFH", blank=True)
    offline_payment_instructions = models.TextField(
        default="You may pay upon arrival in cash (EUR) or by major credit card directly to your private chauffeur or concierge. For bank wire transfers, please transfer funds within 48 hours referencing your Booking Reference.",
        blank=True
    )

    # Site-wide Platform Statistics & Badges
    stat_tours_completed = models.CharField(max_length=50, default="26K+", blank=True, help_text="e.g. 26K+")
    stat_years_experience = models.CharField(max_length=50, default="15+", blank=True, help_text="e.g. 15+")
    stat_happy_travelers = models.CharField(max_length=50, default="15,000+", blank=True, help_text="e.g. 15,000+")
    stat_satisfaction_rate = models.CharField(max_length=50, default="98%", blank=True, help_text="e.g. 98%")
    stat_rating_display = models.CharField(max_length=50, default="4.9", blank=True, help_text="e.g. 4.9")
    partners_title = models.CharField(max_length=200, default="Our 100+ valuable partner in the world-wide", blank=True, help_text="Headline above partner logos marquee on homepage")

    # About Company & Mission Info
    mission_title = models.CharField(max_length=200, default="We're Top Travel Agency in the Nordics.", blank=True)
    mission_description = models.TextField(default="Discover the magic of the Arctic with the experts. We offer unparalleled experiences across the breathtaking landscapes of Finland.", blank=True)
    mission_statement = models.TextField(default="To provide authentic, unforgettable Nordic adventures while promoting sustainable tourism and respecting local traditions.", blank=True)
    vision_statement = models.TextField(default="To be the global benchmark for Arctic travel, ensuring every guest leaves with a deep appreciation for the North.", blank=True)
    founder_name = models.CharField(max_length=100, default="Nord Velocity Team", blank=True)
    founder_title = models.CharField(max_length=100, default="Founder & Managing Director", blank=True)

    # Homepage Explore Section
    explore_badge = models.CharField(
        max_length=200, 
        default="WE'RE #01 TRAVEL AGENCY IN GLOBALLY", 
        blank=True, 
        verbose_name="Explore Subtitle / Badge",
        help_text="Blue small badge text above the main heading"
    )
    explore_title = models.CharField(
        max_length=250, 
        default="Explore the World With Confidence.", 
        blank=True, 
        verbose_name="Explore Main Heading"
    )
    explore_description_1 = models.TextField(
        blank=True, 
        default="Travel is more than visiting places - it's about discovering cultures, creating memories, and experiencing the world in a way that stays with you forever. Our travel agency is dedicated to designing seamless and inspiring journeys for explorers who want more than just a typical vacation.", 
        verbose_name="Short Description (Paragraph 1)"
    )
    explore_description_2 = models.TextField(
        blank=True, 
        default="Our team of passionate travel experts works closely with each traveler to understand their interests, preferences, and expectations. This allows us to create journeys that feel personal, well-organized, and truly extraordinary.", 
        verbose_name="Short Description (Paragraph 2)"
    )
    explore_button_text = models.CharField(
        max_length=100, 
        default="Discover More", 
        blank=True,
        verbose_name="Button Label"
    )
    explore_button_url = models.CharField(
        max_length=255, 
        default="/about/", 
        blank=True,
        verbose_name="Button Link URL"
    )
    explore_image_main = models.ImageField(
        upload_to='site/explore/', 
        blank=True, 
        null=True, 
        verbose_name="Main Center Card Image",
        help_text="Front center card in fanned display (optional, falls back to default if not uploaded)"
    )
    explore_image_left = models.ImageField(
        upload_to='site/explore/', 
        blank=True, 
        null=True, 
        verbose_name="Left Tilted Card Image",
        help_text="Left tilted card in fanned display (optional, falls back to default if not uploaded)"
    )
    explore_image_right = models.ImageField(
        upload_to='site/explore/', 
        blank=True, 
        null=True, 
        verbose_name="Right Tilted Card Image",
        help_text="Right tilted card in fanned display (optional, falls back to default if not uploaded)"
    )
    explore_award_1_count = models.CharField(
        max_length=50,
        default="5,000,000",
        blank=True,
        verbose_name="Award 1 Count (e.g. 15,000+ or 5,000,000)"
    )
    explore_award_1_label = models.CharField(
        max_length=100,
        default="Trusted by 5M Users",
        blank=True,
        verbose_name="Award 1 Label"
    )
    explore_award_2_title = models.CharField(
        max_length=100,
        default="BEST CITY<br>TOUR AWARD",
        blank=True,
        verbose_name="Award 2 Title"
    )
    explore_award_2_year = models.CharField(
        max_length=20,
        default="2025",
        blank=True,
        verbose_name="Award 2 Year"
    )

    # Mobile App Download Section
    app_store_url = models.URLField(blank=True, default="https://apple.com/app-store")
    play_store_url = models.URLField(blank=True, default="https://play.google.com")
    app_rating = models.CharField(max_length=20, default="4.9", blank=True)
    app_reviews_count = models.CharField(max_length=50, default="12,300+", blank=True)
    app_active_users = models.CharField(max_length=50, default="2M+", blank=True)

    maintenance_mode = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

    @property
    def get_explore_image_main_url(self):
        if self.explore_image_main:
            return self.explore_image_main.url
        return '/static/images/explore/explore_2.jpg'

    @property
    def get_explore_image_left_url(self):
        if self.explore_image_left:
            return self.explore_image_left.url
        return '/static/images/explore/explore_1.jpg'

    @property
    def get_explore_image_right_url(self):
        if self.explore_image_right:
            return self.explore_image_right.url
        return '/static/images/explore/explore_3.jpg'

    @property
    def is_youtube_video(self):
        if not self.hero_video_url:
            return False
        return 'youtube.com' in self.hero_video_url or 'youtu.be' in self.hero_video_url

    @property
    def hero_video_embed_url(self):
        if not self.hero_video_url:
            return ""
        import re
        url = self.hero_video_url.strip()
        yt_match = re.search(r'(?:v=|\/embed\/|youtu\.be\/|\/v\/|\/shorts\/)([a-zA-Z0-9_-]{11})', url)
        if yt_match:
            vid_id = yt_match.group(1)
            return f"https://www.youtube.com/embed/{vid_id}?autoplay=1&mute=1&loop=1&playlist={vid_id}&controls=0&playsinline=1"
        return url

    def __str__(self):
        return f"{self.site_name} Configuration"

class FAQItem(models.Model):
    CATEGORY_CHOICES = (
        ('GENERAL', 'General Inquiries'),
        ('TOURS', 'Tours & Experiences'),
        ('CHAUFFEUR', 'Chauffeur & Transfers'),
        ('PAYMENT', 'Booking & Payments'),
        ('WINTER', 'Winter Gear & Weather'),
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='GENERAL')
    question = models.CharField(max_length=300)
    answer = models.TextField()
    sort_order = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.question

class Testimonial(models.Model):
    author_name = models.CharField(max_length=150)
    author_location = models.CharField(max_length=150, help_text="e.g. London, United Kingdom")
    author_avatar = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    tour_name = models.CharField(max_length=200, blank=True, help_text="Tour they experienced")
    rating = models.IntegerField(default=5)
    quote = models.TextField()
    is_featured = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return f"{self.author_name} ({self.rating}★)"


class MediaFile(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='core/media/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Enquiry(models.Model):
    tour = models.ForeignKey('tours.Tour', on_delete=models.CASCADE, related_name='enquiries', null=True, blank=True)
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    message = models.TextField()
    is_replied = models.BooleanField(default=False)
    admin_reply = models.TextField(blank=True, null=True)
    replied_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Enquiries"

    def __str__(self):
        return f"Enquiry from {self.name} - {self.email}"

class ContactSubmission(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=250)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} — {self.name}"


class MegaMenuPromo(models.Model):
    MENU_TYPE_CHOICES = (
        ('DESTINATION', 'Destination Mega Menu Promo'),
        ('COMPANY', 'Company Mega Menu Promo'),
        ('TOUR', 'Tour Mega Menu Promo'),
    )
    menu_type = models.CharField(max_length=20, choices=MENU_TYPE_CHOICES, unique=True)
    badge_text = models.CharField(max_length=50, blank=True, help_text="e.g. 'up to' or '2026'")
    title = models.CharField(max_length=150, help_text="e.g. '30% off SALE' or '2026 Travel Report'")
    subtitle = models.CharField(max_length=200, blank=True, help_text="e.g. 'Winter Packages'")
    description = models.TextField(blank=True, help_text="Promo description copy")
    button_text = models.CharField(max_length=50, default='See Packages')
    button_url = models.CharField(max_length=255, default='/tours/')
    background_image = models.ImageField(upload_to='megamenu/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mega Menu Promo Banner"
        verbose_name_plural = "Mega Menu Promo Banners"

    def __str__(self):
        return f"{self.get_menu_type_display()} - {self.title}"


class CompanyMenuItem(models.Model):
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=255, default='#')
    image = models.ImageField(upload_to='company_nav/', blank=True, null=True, help_text="Circle thumbnail image")
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Company Menu Item"
        verbose_name_plural = "Company Menu Items"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class HomeOfferCard(models.Model):
    title = models.CharField(max_length=150, blank=True, help_text="Headline e.g. NORDIC WINTER WONDERLAND")
    subtitle = models.CharField(max_length=150, blank=True, help_text="Subtitle e.g. Lapland Snowmobile & Husky Safari")
    badge_text = models.CharField(max_length=50, blank=True, help_text="Pink pill badge text e.g. 25% off")
    price_badge = models.CharField(max_length=50, blank=True, help_text="Red circular badge at bottom right e.g. $199/only or SALE")
    image = models.ImageField(upload_to='offers/', blank=True, null=True, help_text="Card background image upload")
    url = models.CharField(max_length=255, default='/tours/', blank=True, help_text="Link destination when card is clicked")
    sort_order = models.IntegerField(default=0, help_text="Display position (0, 1, 2, 3...)")
    is_active = models.BooleanField(default=True, help_text="Toggle card visibility on homepage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Discounts & Offers Card"
        verbose_name_plural = "Discounts & Offers Cards (Homepage)"
        ordering = ['sort_order', 'id']

    @property
    def price_main(self):
        if not self.price_badge:
            return ""
        text = self.price_badge.strip()
        if '/' in text:
            return text.split('/', 1)[0].strip()
        if ' ' in text and not text.upper().startswith(('UP', 'FROM', 'SAVE')):
            return text.split(' ', 1)[0].strip()
        return text

    @property
    def price_sub(self):
        if not self.price_badge:
            return ""
        text = self.price_badge.strip()
        if '/' in text:
            return text.split('/', 1)[1].strip()
        if ' ' in text and not text.upper().startswith(('UP', 'FROM', 'SAVE')):
            return text.split(' ', 1)[1].strip()
        return ""

    def __str__(self):
        return self.title or f"Offer Card #{self.id}"


class PartnerLogo(models.Model):
    name = models.CharField(max_length=150)
    logo_image = models.ImageField(upload_to='partners/', blank=True, null=True)
    url = models.CharField(max_length=255, default='#', blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Partner / Sponsor Logo"
        verbose_name_plural = "Partner / Sponsor Logos"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, help_text="e.g. CEO & Founder, Head of Arctic Operations")
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Leadership Team Member"
        verbose_name_plural = "Leadership Team Members"
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f"{self.name} - {self.role}"


class ValueProposition(models.Model):
    title = models.CharField(max_length=150, help_text="e.g. Best Price Guarantee")
    description = models.TextField()
    icon_class = models.CharField(max_length=100, default='ph-bold ph-star', help_text="Phosphor icon class")
    bg_color_class = models.CharField(max_length=50, default='bg-light-green', help_text="e.g. bg-light-green, bg-light-gray, bg-light-teal, bg-light-purple")
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Value Proposition / Feature"
        verbose_name_plural = "Value Propositions / Features"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title


class NavbarItem(models.Model):
    MENU_TYPE_CHOICES = (
        ('NONE', 'Direct Link (No Menu)'),
        ('DESTINATION', 'Destination Mega Menu'),
        ('COMPANY', 'Company Mega Menu'),
        ('TOUR', 'Tour Mega Menu'),
    )
    title = models.CharField(max_length=100, help_text="Navigation link label e.g. Home, Destination, Company, Tour, Transport, Contact")
    url = models.CharField(max_length=255, default='/', help_text="Target URL or path")
    icon = models.ImageField(upload_to='navbar/icons/', blank=True, null=True, help_text="Upload nav icon image (SVG/PNG) managed from admin panel")
    menu_type = models.CharField(max_length=20, choices=MENU_TYPE_CHOICES, default='NONE', help_text="Attach a mega menu if applicable")
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Navbar Item"
        verbose_name_plural = "Navbar Items"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.title} ({self.get_menu_type_display()})"

