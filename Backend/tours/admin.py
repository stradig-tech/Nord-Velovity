from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import (
    Country, Destination, Season, ExperienceType, TravelStyle, DurationBand,
    Tour, TourMedia, TourHighlight, TourItinerary, TourInclusion, 
    TourFAQ, TourPickup, TourDate, TourPricing, TourReview, RelatedTour,
    TourCategory, TourSurrounding, TourExtraService, Wishlist,
    VehicleType, TourOptionPricing, Departure, DepartureCapacity
)

# --- Taxonomy Admins ---

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'flag_preview', 'region', 'destinations_count', 'packages_count', 'is_featured_in_nav', 'is_active', 'sort_order')
    list_filter = ('is_featured_in_nav', 'is_active', 'region')
    search_fields = ('name', 'subtitle', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured_in_nav', 'is_active', 'sort_order')

    def flag_preview(self, obj):
        if obj.flag_icon:
            return mark_safe(f'<img src="{obj.flag_icon.url}" style="height: 22px; width: 32px; object-fit: cover; border-radius: 3px; border: 1px solid #CBD5E1;">')
        return mark_safe('<span style="color: #94A3B8; font-size: 0.8rem;">No flag</span>')
    flag_preview.short_description = "Flag Icon"

    def destinations_count(self, obj):
        return obj.destinations.count()
    destinations_count.short_description = "Tour Places"

    def packages_count(self, obj):
        return Tour.objects.filter(destination__country=obj).count()
    packages_count.short_description = "Packages"


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'flag_preview', 'country', 'packages_count', 'circle_preview', 'is_featured_in_nav', 'is_active', 'sort_order')
    list_filter = ('is_featured_in_nav', 'is_active', 'country')
    search_fields = ('name', 'country__name', 'description', 'highlights')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured_in_nav', 'is_active', 'sort_order')

    def flag_preview(self, obj):
        url = obj.get_flag_url
        if url:
            return mark_safe(f'<img src="{url}" style="height: 18px; width: 28px; object-fit: cover; border-radius: 2px; border: 1px solid #CBD5E1;">')
        return mark_safe('<span style="color: #94A3B8; font-size: 0.8rem;">No flag</span>')
    flag_preview.short_description = "Flag"

    def packages_count(self, obj):
        return obj.tours.count()
    packages_count.short_description = "Packages"

    def circle_preview(self, obj):
        img_url = obj.nav_icon.url if obj.nav_icon else (obj.hero_image.url if obj.hero_image else None)
        if img_url:
            return mark_safe(f'<img src="{img_url}" style="height: 38px; width: 38px; border-radius: 50%; object-fit: cover; border: 2px solid #E2E8F0;">')
        return mark_safe('<span style="color: #94A3B8; font-size: 0.8rem;">No icon</span>')
    circle_preview.short_description = "Nav Icon"


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ExperienceType)
class ExperienceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'circle_preview', 'is_featured_in_nav', 'sort_order')
    list_editable = ('is_featured_in_nav', 'sort_order')
    list_filter = ('is_featured_in_nav',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def circle_preview(self, obj):
        img_url = obj.nav_icon.url if obj.nav_icon else (obj.image.url if obj.image else None)
        if img_url:
            return mark_safe(f'<img src="{img_url}" style="height: 38px; width: 38px; border-radius: 50%; object-fit: cover; border: 2px solid #E2E8F0;">')
        return mark_safe('<span style="color: #94A3B8; font-size: 0.8rem;">No icon</span>')
    circle_preview.short_description = "Nav Icon"


@admin.register(TravelStyle)
class TravelStyleAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(DurationBand)
class DurationBandAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_hours', 'max_hours')
    prepopulated_fields = {'slug': ('name',)}


# --- Tour Inlines ---

class TourMediaInline(admin.TabularInline):
    model = TourMedia
    extra = 1
    fields = ('image_preview', 'file', 'alt_text', 'media_type', 'is_hero', 'sort_order')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.file and obj.media_type == 'IMAGE':
            return mark_safe(f'<img src="{obj.file.url}" style="height:80px; width:120px; object-fit:cover; border-radius:6px; border:1px solid #E2E8F0;">')
        elif obj.file and obj.media_type == 'VIDEO':
            return mark_safe('<span style="color:#6366F1; font-weight:600;">🎬 Video</span>')
        return mark_safe('<span style="color:#94A3B8; font-size:0.85rem;">No preview</span>')
    image_preview.short_description = "Preview"


class TourHighlightInline(admin.TabularInline):
    model = TourHighlight
    extra = 1


class TourItineraryInline(admin.StackedInline):
    model = TourItinerary
    extra = 1
    readonly_fields = ('itinerary_image_preview',)

    def itinerary_image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="height:80px; width:120px; object-fit:cover; border-radius:6px; border:1px solid #E2E8F0;">')
        return mark_safe('<span style="color:#94A3B8; font-size:0.85rem;">No image uploaded</span>')
    itinerary_image_preview.short_description = "Image Preview"


class TourInclusionInline(admin.TabularInline):
    model = TourInclusion
    extra = 1


class TourFAQInline(admin.StackedInline):
    model = TourFAQ
    extra = 1


class TourPickupInline(admin.TabularInline):
    model = TourPickup
    extra = 1


class TourDateInline(admin.TabularInline):
    model = TourDate
    extra = 1


class TourOptionPricingInline(admin.TabularInline):
    model = TourOptionPricing
    extra = 1
    fields = ('vehicle_type', 'adult_price', 'child_price', 'currency', 'early_bird_price', 'early_bird_deadline', 'is_active')


class TourPricingInline(admin.TabularInline):
    model = TourPricing
    extra = 1


class TourSurroundingInline(admin.TabularInline):
    model = TourSurrounding
    extra = 1


class TourExtraServiceInline(admin.TabularInline):
    model = TourExtraService
    extra = 1


@admin.register(TourCategory)
class TourCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_thumbnail', 'parent', 'is_active', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)

    def category_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="height:40px; width:60px; object-fit:cover; border-radius:6px; border:1px solid #CBD5E1;">')
        return mark_safe('<span style="color:#94A3B8; font-size:0.8rem;">No image</span>')
    category_thumbnail.short_description = "Image"


# --- Main Tour Admin ---

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('title', 'tour_thumbnail', 'destination', 'is_group_tour', 'is_private_tour', 'is_family_tour', 'status', 'is_featured')
    list_filter = ('status', 'is_featured', 'guarantee_policy', 'has_guaranteed_reattempt', 'is_group_tour', 'is_private_tour', 'is_family_tour', 'destination', 'travel_style')
    list_editable = ('status', 'is_featured', 'is_group_tour', 'is_private_tour', 'is_family_tour')
    search_fields = ('title', 'short_summary')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [
        TourMediaInline, TourHighlightInline, TourItineraryInline,
        TourInclusionInline, TourFAQInline, TourPickupInline,
        TourOptionPricingInline, TourPricingInline, TourExtraServiceInline, TourDateInline, TourSurroundingInline
    ]
    filter_horizontal = ('seasons', 'experience_types')
    actions = ['duplicate_tour']

    def tour_thumbnail(self, obj):
        hero = obj.media.filter(is_hero=True).first() or obj.media.first()
        if hero and hero.file:
            return mark_safe(f'<img src="{hero.file.url}" style="height:40px; width:60px; object-fit:cover; border-radius:6px; border:1px solid #CBD5E1;">')
        return mark_safe('<span style="color:#94A3B8; font-size:0.8rem;">No image</span>')
    tour_thumbnail.short_description = "Photo"

    @admin.action(description="📋 Duplicate selected tour(s) with all itineraries & pricing")
    def duplicate_tour(self, request, queryset):
        import uuid
        duplicated_count = 0
        for tour in queryset:
            seasons = list(tour.seasons.all())
            experience_types = list(tour.experience_types.all())

            old_tour_id = tour.id
            old_tour = Tour.objects.get(id=old_tour_id)
            
            tour.pk = None
            tour.id = None
            short_suffix = uuid.uuid4().hex[:4]
            tour.slug = f"{old_tour.slug}-copy-{short_suffix}"
            tour.title = f"Copy of {old_tour.title}"
            tour.status = 'DRAFT'
            tour.save()

            tour.seasons.set(seasons)
            tour.experience_types.set(experience_types)

            for m in old_tour.media.all():
                m.pk = None; m.tour = tour; m.save()
            for h in old_tour.highlights.all():
                h.pk = None; h.tour = tour; h.save()
            for it in old_tour.itinerary.all():
                it.pk = None; it.tour = tour; it.save()
            for inc in old_tour.inclusions.all():
                inc.pk = None; inc.tour = tour; inc.save()
            for faq in old_tour.faqs.all():
                faq.pk = None; faq.tour = tour; faq.save()
            for p in old_tour.pricing.all():
                p.pk = None; p.tour = tour; p.save()
            for extra in old_tour.extra_services.all():
                extra.pk = None; extra.tour = tour; extra.save()
            for pick in old_tour.pickups.all():
                pick.pk = None; pick.tour = tour; pick.save()
            for surr in old_tour.surroundings.all():
                surr.pk = None; surr.tour = tour; surr.save()
            for op in old_tour.option_pricing.all():
                op.pk = None; op.tour = tour; op.save()

            duplicated_count += 1

        self.message_user(request, f"{duplicated_count} tour(s) duplicated successfully with all itineraries, inclusions, and pricing as Drafts.")


@admin.register(TourDate)
class TourDateAdmin(admin.ModelAdmin):
    list_display = ('tour', 'tour_date_thumbnail', 'start_date', 'end_date', 'total_capacity', 'booked_count', 'available_seats', 'status')
    list_filter = ('status', 'start_date', 'tour')
    list_editable = ('total_capacity', 'status')
    search_fields = ('tour__title', 'notes')
    ordering = ('start_date',)
    date_hierarchy = 'start_date'

    def tour_date_thumbnail(self, obj):
        hero = obj.tour.media.filter(is_hero=True).first() or obj.tour.media.first()
        if hero and hero.file:
            return mark_safe(f'<img src="{hero.file.url}" style="height:40px; width:60px; object-fit:cover; border-radius:6px; border:1px solid #CBD5E1;">')
        return mark_safe('<span style="color:#94A3B8; font-size:0.8rem;">No image</span>')
    tour_date_thumbnail.short_description = "Photo"

    def available_seats(self, obj):
        rem = obj.total_capacity - obj.booked_count
        if rem <= 0:
            return "0 (Sold Out)"
        return f"{rem} seats"
    available_seats.short_description = "Available"


@admin.register(TourPricing)
class TourPricingAdmin(admin.ModelAdmin):
    list_display = ('tour', 'label', 'price', 'currency', 'season', 'early_bird_price', 'early_bird_deadline')
    list_filter = ('currency', 'season', 'label')
    list_editable = ('price',)
    search_fields = ('tour__title', 'label')


@admin.register(TourReview)
class TourReviewAdmin(admin.ModelAdmin):
    list_display = ('tour', 'customer', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'tour', 'created_at')
    search_fields = ('user__email', 'tour__title')


# --- Central OTA Departure & Capacity Admins ---

@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'default_capacity', 'sort_order', 'is_active')
    list_editable = ('icon', 'default_capacity', 'sort_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'default_capacity')


@admin.register(TourOptionPricing)
class TourOptionPricingAdmin(admin.ModelAdmin):
    list_display = ('tour', 'vehicle_type', 'adult_price', 'child_price', 'currency', 'early_bird_price', 'is_active')
    list_filter = ('vehicle_type', 'is_active', 'tour')
    list_editable = ('adult_price', 'child_price', 'is_active')
    search_fields = ('tour__title', 'vehicle_type__name')
    ordering = ('tour', 'vehicle_type__sort_order')


class DepartureCapacityForm(forms.ModelForm):
    class Meta:
        model = DepartureCapacity
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'total_capacity' in self.fields:
            self.fields['total_capacity'].required = False

    def clean(self):
        cleaned_data = super().clean()
        vt = cleaned_data.get('vehicle_type')
        tot = cleaned_data.get('total_capacity')
        if vt and (tot is None or tot == ''):
            cleaned_data['total_capacity'] = vt.default_capacity or 12
        return cleaned_data

    def validate_unique(self):
        if not self.instance.pk:
            dep = self.cleaned_data.get('departure') or getattr(self.instance, 'departure', None)
            vt = self.cleaned_data.get('vehicle_type')
            if dep and vt:
                existing = DepartureCapacity.objects.filter(departure=dep, vehicle_type=vt).first()
                if existing:
                    self.instance = existing
                    return
        super().validate_unique()


class DepartureCapacityInline(admin.TabularInline):
    model = DepartureCapacity
    form = DepartureCapacityForm
    extra = 1
    max_num = 3
    fields = ('vehicle_type', 'total_capacity', 'booked_count', 'blocked_seats', 'reattempt_reserved', 'price_override_adult', 'price_override_child', 'sellable_display')
    readonly_fields = ('sellable_display',)

    def sellable_display(self, obj):
        if obj.id:
            rem = obj.public_sellable
            if rem <= 0:
                return mark_safe('<span style="color:#EF4444; font-weight:700;">SOLD OUT (0)</span>')
            return mark_safe(f'<span style="color:#10B981; font-weight:700;">{rem} seats</span>')
        return "-"
    sellable_display.short_description = "Sellable"


@admin.register(Departure)
class DepartureAdmin(admin.ModelAdmin):
    list_display = ('tour', 'date', 'time', 'status', 'capacity_overview', 'created_at')
    list_filter = ('status', 'date', 'tour')
    list_editable = ('status',)
    search_fields = ('tour__title', 'notes')
    ordering = ('date', 'time')
    date_hierarchy = 'date'
    inlines = [DepartureCapacityInline]

    def capacity_overview(self, obj):
        caps = obj.capacities.select_related('vehicle_type').all()
        if not caps:
            return mark_safe('<span style="color:#94A3B8;">No capacities set</span>')
        badges = []
        for c in caps:
            icon = c.vehicle_type.icon or '🚗'
            color = '#EF4444' if c.is_sold_out else '#10B981'
            badges.append(
                f'<span style="display:inline-block; margin-right:8px; padding:2px 8px; border-radius:4px; '
                f'background:#F1F5F9; font-size:0.8rem; border:1px solid #E2E8F0;">'
                f'{icon} {c.vehicle_type.name}: <strong style="color:{color};">{c.public_sellable}/{c.total_capacity}</strong></span>'
            )
        return mark_safe(''.join(badges))
    capacity_overview.short_description = "Capacity (Sellable / Total)"

    def change_view(self, request, object_id, form_url='', extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and obj.capacities.count() == 0:
            obj.auto_init_capacities()
        return super().change_view(request, object_id, form_url, extra_context)
