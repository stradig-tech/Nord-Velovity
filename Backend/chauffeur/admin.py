from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import (
    VehicleClass, Vehicle, VehiclePhoto, PricingRule, 
    FixedRoute, Zone, Surcharge, AvailabilityRule,
    ChauffeurServiceStandard, ChauffeurInclusion, ChauffeurSafetyStandard
)

class VehiclePhotoInline(admin.TabularInline):
    model = VehiclePhoto
    extra = 1
    fields = ('photo_preview', 'image_file', 'alt_text', 'is_primary', 'sort_order')
    readonly_fields = ('photo_preview',)

    def photo_preview(self, obj):
        if obj and obj.image_file:
            return mark_safe(f'<img src="{obj.image_file.url}" style="height:70px; width:110px; object-fit:cover; border-radius:6px; border:1px solid #E2E8F0; box-shadow:0 1px 3px rgba(0,0,0,0.1);">')
        return mark_safe('<span style="color:#94A3B8; font-size:0.85rem;">No preview</span>')
    photo_preview.short_description = "Preview"


class ChauffeurServiceStandardInline(admin.TabularInline):
    model = ChauffeurServiceStandard
    extra = 1
    fields = ('title', 'sort_order', 'is_active')


class ChauffeurInclusionInline(admin.TabularInline):
    model = ChauffeurInclusion
    extra = 1
    fields = ('text', 'is_included', 'sort_order', 'is_active')


class ChauffeurSafetyStandardInline(admin.TabularInline):
    model = ChauffeurSafetyStandard
    extra = 1
    fields = ('text', 'sort_order', 'is_active')


class PricingRuleInline(admin.TabularInline):
    model = PricingRule
    extra = 0
    fields = ('base_fare', 'per_km_rate', 'minimum_fare', 'hourly_rate', 'currency', 'is_active', 'valid_from')


@admin.register(VehicleClass)
class VehicleClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'class_thumbnail', 'vehicles_count', 'sort_order', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [
        PricingRuleInline, 
        VehiclePhotoInline, 
        ChauffeurServiceStandardInline, 
        ChauffeurInclusionInline, 
        ChauffeurSafetyStandardInline
    ]

    def class_thumbnail(self, obj):
        photo = obj.photos.filter(is_primary=True).first() or obj.photos.first()
        if not photo:
            first_v = obj.vehicles.first()
            if first_v:
                photo = first_v.photos.filter(is_primary=True).first() or first_v.photos.first()
        if photo and photo.image_file:
            return mark_safe(f'<img src="{photo.image_file.url}" style="height:40px; width:65px; object-fit:cover; border-radius:6px; border:1px solid #CBD5E1;">')
        return mark_safe('<span style="color:#94A3B8; font-size:0.8rem;">No photo</span>')
    class_thumbnail.short_description = "Preview"

    def vehicles_count(self, obj):
        count = obj.vehicles.count()
        return mark_safe(f'<strong>{count}</strong> vehicle(s)')
    vehicles_count.short_description = "Fleet Size"


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'vehicle_thumbnail', 'vehicle_class', 'passenger_capacity', 'is_active')
    list_filter = ('vehicle_class', 'is_active')
    search_fields = ('name',)
    inlines = [VehiclePhotoInline]

    def vehicle_thumbnail(self, obj):
        photo = obj.photos.filter(is_primary=True).first() or obj.photos.first()
        if photo and photo.image_file:
            return mark_safe(f'<img src="{photo.image_file.url}" style="height:40px; width:60px; object-fit:cover; border-radius:6px; border:1px solid #CBD5E1;">')
        return mark_safe('<span style="color:#94A3B8; font-size:0.8rem;">No photo</span>')
    vehicle_thumbnail.short_description = "Photo"


@admin.register(VehiclePhoto)
class VehiclePhotoAdmin(admin.ModelAdmin):
    list_display = ('photo_preview', 'target_assigned', 'is_primary', 'sort_order', 'alt_text')
    list_filter = ('vehicle_class', 'vehicle', 'is_primary')
    search_fields = ('alt_text', 'vehicle__name', 'vehicle_class__name')
    list_editable = ('is_primary', 'sort_order')

    def photo_preview(self, obj):
        if obj.image_file:
            return mark_safe(f'<img src="{obj.image_file.url}" style="height:60px; width:95px; object-fit:cover; border-radius:6px; border:1px solid #E2E8F0;">')
        return mark_safe('<span style="color:#94A3B8; font-size:0.8rem;">No photo</span>')
    photo_preview.short_description = "Preview"

    def target_assigned(self, obj):
        if obj.vehicle:
            return mark_safe(f'<strong>Vehicle:</strong> {obj.vehicle.name} <span style="color:#64748B;">({obj.vehicle.vehicle_class.name})</span>')
        elif obj.vehicle_class:
            return mark_safe(f'<strong>Class:</strong> {obj.vehicle_class.name}')
        return mark_safe('<span style="color:#94A3B8;">Unassigned</span>')
    target_assigned.short_description = "Assigned To"


@admin.register(ChauffeurServiceStandard)
class ChauffeurServiceStandardAdmin(admin.ModelAdmin):
    list_display = ('title', 'scope_badge', 'sort_order', 'is_active')
    list_filter = ('vehicle_class', 'is_active')
    search_fields = ('title',)
    list_editable = ('sort_order', 'is_active')

    def scope_badge(self, obj):
        if obj.vehicle_class:
            return mark_safe(f'<span style="background:#EEF2FF; color:#4F46E5; padding:3px 8px; border-radius:4px; font-weight:600; font-size:0.8rem;">{obj.vehicle_class.name}</span>')
        return mark_safe('<span style="background:#F1F5F9; color:#475569; padding:3px 8px; border-radius:4px; font-weight:600; font-size:0.8rem;">🌐 Global (All Classes)</span>')
    scope_badge.short_description = "Applies To"


@admin.register(ChauffeurInclusion)
class ChauffeurInclusionAdmin(admin.ModelAdmin):
    list_display = ('text', 'status_badge', 'scope_badge', 'sort_order', 'is_active')
    list_filter = ('is_included', 'vehicle_class', 'is_active')
    search_fields = ('text',)
    list_editable = ('sort_order', 'is_active')

    def status_badge(self, obj):
        if obj.is_included:
            return mark_safe('<span style="background:#DCFCE7; color:#16A34A; padding:3px 8px; border-radius:4px; font-weight:600; font-size:0.8rem;">✓ Included in Price</span>')
        return mark_safe('<span style="background:#FEE2E2; color:#DC2626; padding:3px 8px; border-radius:4px; font-weight:600; font-size:0.8rem;">✗ Extra Charge</span>')
    status_badge.short_description = "Type"

    def scope_badge(self, obj):
        if obj.vehicle_class:
            return mark_safe(f'<span style="background:#EEF2FF; color:#4F46E5; padding:3px 8px; border-radius:4px; font-weight:600; font-size:0.8rem;">{obj.vehicle_class.name}</span>')
        return mark_safe('<span style="background:#F1F5F9; color:#475569; padding:3px 8px; border-radius:4px; font-weight:600; font-size:0.8rem;">🌐 Global (All Classes)</span>')
    scope_badge.short_description = "Applies To"


@admin.register(ChauffeurSafetyStandard)
class ChauffeurSafetyStandardAdmin(admin.ModelAdmin):
    list_display = ('text', 'scope_badge', 'sort_order', 'is_active')
    list_filter = ('vehicle_class', 'is_active')
    search_fields = ('text',)
    list_editable = ('sort_order', 'is_active')

    def scope_badge(self, obj):
        if obj.vehicle_class:
            return mark_safe(f'<span style="background:#EEF2FF; color:#4F46E5; padding:3px 8px; border-radius:4px; font-weight:600; font-size:0.8rem;">{obj.vehicle_class.name}</span>')
        return mark_safe('<span style="background:#F1F5F9; color:#475569; padding:3px 8px; border-radius:4px; font-weight:600; font-size:0.8rem;">🌐 Global (All Classes)</span>')
    scope_badge.short_description = "Applies To"


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_class', 'base_fare', 'per_km_rate', 'minimum_fare', 'hourly_rate', 'is_active')
    list_filter = ('is_active', 'vehicle_class')


@admin.register(FixedRoute)
class FixedRouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'vehicle_class', 'fixed_price', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active', 'vehicle_class')


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'surcharge_amount', 'surcharge_type', 'is_active')


@admin.register(Surcharge)
class SurchargeAdmin(admin.ModelAdmin):
    list_display = ('name', 'surcharge_category', 'amount', 'is_active')
    list_filter = ('surcharge_category', 'is_active')


@admin.register(AvailabilityRule)
class AvailabilityRuleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_class', 'day_of_week', 'start_time', 'end_time', 'is_available')
