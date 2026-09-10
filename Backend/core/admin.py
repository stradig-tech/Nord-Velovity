from django.contrib import admin
from .models import (
    AuditLog, SiteSetting, MediaFile, Enquiry, ContactSubmission, 
    FAQItem, Testimonial, MegaMenuPromo, CompanyMenuItem,
    HomeOfferCard, PartnerLogo, TeamMember, ValueProposition, NavbarItem
)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'model_name', 'object_repr')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__email', 'object_repr')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'ip_address', 'timestamp')
    
    def has_add_permission(self, request):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False

from django.utils.safestring import mark_safe

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'logo_thumbnail', 'contact_phone', 'contact_email', 'default_currency', 'maintenance_mode', 'updated_at')
    readonly_fields = (
        'logo_preview', 'favicon_preview', 'preview_image_display',
        'explore_image_left_preview', 'explore_image_main_preview', 'explore_image_right_preview'
    )
    
    fieldsets = (
        ("Brand & Identity", {
            'fields': (
                ('site_name', 'tagline'),
                ('logo', 'favicon'),
                ('logo_preview', 'favicon_preview'),
                'preview_image',
                'preview_image_display',
            )
        }),
        ("🌟 Homepage Hero Section (Text, Video Link & Background)", {
            'description': "Manage the main headline, description, background YouTube video link, or uploaded MP4 background video.",
            'fields': (
                'hero_title',
                'hero_subtitle',
                'hero_video_url',
                ('hero_video_file', 'hero_background_image'),
            )
        }),
        ("🌍 Homepage Explore Section (Heading, Descriptions, Button & Fanned Images)", {
            'description': "Manage the 'Explore the World With Confidence' section on the homepage including titles, paragraphs, images, and award badges.",
            'fields': (
                ('explore_badge', 'explore_title'),
                'explore_description_1',
                'explore_description_2',
                ('explore_button_text', 'explore_button_url'),
                ('explore_image_left', 'explore_image_main', 'explore_image_right'),
                ('explore_image_left_preview', 'explore_image_main_preview', 'explore_image_right_preview'),
                ('explore_award_1_count', 'explore_award_1_label'),
                ('explore_award_2_title', 'explore_award_2_year'),
            )
        }),
        ("Platform Statistics & Partners Section", {
            'fields': (
                ('stat_tours_completed', 'stat_years_experience'),
                ('stat_happy_travelers', 'stat_satisfaction_rate'),
                'stat_rating_display',
                'partners_title',
            )
        }),
        ("About Company, Mission & Founder", {
            'fields': (
                'mission_title',
                'mission_description',
                'mission_statement',
                'vision_statement',
                ('founder_name', 'founder_title')
            )
        }),
        ("Mobile App Settings", {
            'fields': (
                ('app_store_url', 'play_store_url'),
                ('app_rating', 'app_reviews_count', 'app_active_users')
            )
        }),
        ("Contact & Location", {
            'fields': ('contact_phone', 'emergency_phone', 'contact_email', 'office_address', 'operating_hours', 'google_maps_embed_url')
        }),
        ("Currency & Rates", {
            'fields': ('default_currency', 'currency_symbol')
        }),
        ("Social Profiles", {
            'fields': ('facebook_url', 'instagram_url', 'linkedin_url', 'tripadvisor_url')
        }),
        ("Footer & Legal", {
            'fields': ('footer_text', 'copyright_text')
        }),
        ("System Status", {
            'fields': ('maintenance_mode',)
        }),
    )

    def logo_thumbnail(self, obj):
        url = obj.logo.url if obj.logo else "/static/images/brand/logo%20bg-transparent.png"
        return mark_safe(f'<div style="background: #0f172a; border-radius: 4px; padding: 2px 6px; display: inline-block;"><img src="{url}" style="height: 22px; max-width: 80px; object-fit: contain;" /></div>')
    logo_thumbnail.short_description = "Logo"

    def logo_preview(self, obj):
        if obj and obj.logo:
            return mark_safe(f'''
                <div style="background: #0f172a; padding: 10px 16px; border-radius: 8px; display: inline-flex; align-items: center; gap: 12px; border: 1px solid #334155;">
                    <img src="{obj.logo.url}" style="max-height: 44px; max-width: 160px; object-fit: contain;" />
                    <span style="color: #38bdf8; font-size: 11px; font-weight: 700; text-transform: uppercase;">Active Logo</span>
                </div>
            ''')
        return mark_safe('''
            <div style="background: #0f172a; padding: 10px 16px; border-radius: 8px; display: inline-flex; align-items: center; gap: 12px; border: 1px solid #334155;">
                <img src="/static/images/brand/logo%20bg-transparent.png" style="max-height: 44px; max-width: 160px; object-fit: contain;" />
                <span style="color: #94a3b8; font-size: 11px; font-weight: 500;">Default Static Logo</span>
            </div>
        ''')
    logo_preview.short_description = "Logo Preview"

    def favicon_preview(self, obj):
        if obj and obj.favicon:
            return mark_safe(f'''
                <div style="background: #ffffff; padding: 8px 14px; border-radius: 8px; display: inline-flex; align-items: center; gap: 10px; border: 1.5px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    <img src="{obj.favicon.url}" style="width: 28px; height: 28px; object-fit: contain;" />
                    <span style="color: #0f172a; font-size: 11px; font-weight: 700;">Active Favicon</span>
                </div>
            ''')
        return mark_safe('''
            <div style="background: #ffffff; padding: 8px 14px; border-radius: 8px; display: inline-flex; align-items: center; gap: 10px; border: 1.5px solid #cbd5e1; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <img src="/static/images/brand/logo%20bg-transparent.png" style="width: 28px; height: 28px; object-fit: contain;" />
                <span style="color: #94a3b8; font-size: 11px; font-weight: 500;">Default Favicon</span>
            </div>
        ''')
    favicon_preview.short_description = "Favicon Preview"

    def preview_image_display(self, obj):
        if obj and obj.preview_image:
            return mark_safe(f'''
                <div style="border-radius: 8px; overflow: hidden; display: inline-block; max-width: 320px; border: 1px solid #cbd5e1; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <img src="{obj.preview_image.url}" style="width: 100%; max-height: 160px; object-fit: cover; display: block;" />
                    <div style="background: #f8fafc; padding: 6px 10px; font-size: 11px; color: #475569; font-weight: 600;">Active Social / OG Preview Image</div>
                </div>
            ''')
        return mark_safe('<span style="color: #94a3b8; font-style: italic;">No OG image uploaded (default: blank)</span>')
    preview_image_display.short_description = "OG Image Preview"

    def explore_image_main_preview(self, obj):
        url = obj.get_explore_image_main_url if obj else '/static/images/explore/explore_2.jpg'
        return mark_safe(f'''
            <div style="display: inline-flex; flex-direction: column; align-items: center; gap: 6px; padding: 8px; background: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0;">
                <img src="{url}" style="height: 75px; width: 110px; object-fit: cover; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />
                <span style="font-size: 11px; color: #475569; font-weight: 700;">Center Card (Front)</span>
            </div>
        ''')
    explore_image_main_preview.short_description = "Center Card Preview"

    def explore_image_left_preview(self, obj):
        url = obj.get_explore_image_left_url if obj else '/static/images/explore/explore_1.jpg'
        return mark_safe(f'''
            <div style="display: inline-flex; flex-direction: column; align-items: center; gap: 6px; padding: 8px; background: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0;">
                <img src="{url}" style="height: 75px; width: 110px; object-fit: cover; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />
                <span style="font-size: 11px; color: #475569; font-weight: 700;">Left Card</span>
            </div>
        ''')
    explore_image_left_preview.short_description = "Left Card Preview"

    def explore_image_right_preview(self, obj):
        url = obj.get_explore_image_right_url if obj else '/static/images/explore/explore_3.jpg'
        return mark_safe(f'''
            <div style="display: inline-flex; flex-direction: column; align-items: center; gap: 6px; padding: 8px; background: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0;">
                <img src="{url}" style="height: 75px; width: 110px; object-fit: cover; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);" />
                <span style="font-size: 11px; color: #475569; font-weight: 700;">Right Card</span>
            </div>
        ''')
    explore_image_right_preview.short_description = "Right Card Preview"

    def has_add_permission(self, request):
        # Only allow 1 settings file to ever exist
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)

@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'sort_order', 'is_published', 'created_at')
    list_filter = ('category', 'is_published')
    search_fields = ('question', 'answer')
    list_editable = ('sort_order', 'is_published')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'avatar_preview', 'author_location', 'rating', 'is_featured', 'sort_order')
    list_filter = ('rating', 'is_featured')
    search_fields = ('author_name', 'quote', 'tour_name')
    list_editable = ('is_featured', 'sort_order')

    def avatar_preview(self, obj):
        if obj.author_avatar:
            return mark_safe(f'<img src="{obj.author_avatar.url}" style="height:40px; width:40px; border-radius:50%; object-fit:cover; border:2px solid #E2E8F0;">')
        return mark_safe('<span style="color:#94A3B8; font-size:0.8rem;">No avatar</span>')
    avatar_preview.short_description = "Avatar"


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_preview', 'uploaded_at')
    search_fields = ('title',)

    def file_preview(self, obj):
        if obj.file:
            url = obj.file.url.lower()
            if any(url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
                return mark_safe(f'<img src="{obj.file.url}" style="height:40px; width:60px; object-fit:cover; border-radius:6px; border:1px solid #CBD5E1;">')
            return mark_safe(f'<span style="color:#6366F1; font-weight:600;">📄 {url.split(".")[-1].upper()}</span>')
        return mark_safe('<span style="color:#94A3B8; font-size:0.8rem;">No file</span>')
    file_preview.short_description = "Preview"

@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'tour', 'is_replied', 'created_at')
    list_filter = ('is_replied', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at', 'replied_at')

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)


from .models import MegaMenuPromo, CompanyMenuItem

@admin.register(MegaMenuPromo)
class MegaMenuPromoAdmin(admin.ModelAdmin):
    list_display = ('menu_type', 'title', 'banner_preview', 'button_text', 'button_url', 'is_active', 'updated_at')
    list_editable = ('is_active',)
    list_filter = ('menu_type', 'is_active')
    search_fields = ('title', 'subtitle', 'description')
    readonly_fields = ('banner_preview_display',)

    fieldsets = (
        ("Menu Placement & Visibility", {
            'fields': (('menu_type', 'is_active'),)
        }),
        ("Promotional Messaging", {
            'fields': (
                ('badge_text', 'title'),
                'subtitle',
                'description',
                ('button_text', 'button_url')
            )
        }),
        ("Banner Visuals", {
            'fields': ('background_image', 'banner_preview_display')
        })
    )

    def banner_preview(self, obj):
        if obj.background_image:
            return mark_safe(f'<img src="{obj.background_image.url}" style="height: 40px; width: 60px; object-fit: cover; border-radius: 6px; border: 1px solid #CBD5E1;">')
        return mark_safe('<span style="color: #94A3B8; font-size: 0.8rem; font-style: italic;">No banner image</span>')
    banner_preview.short_description = "Banner"

    def banner_preview_display(self, obj):
        if obj and obj.background_image:
            return mark_safe(f'''
                <div style="background: url('{obj.background_image.url}') center/cover no-repeat; border-radius: 12px; padding: 1.5rem; max-width: 320px; color: white; min-height: 200px; display: flex; flex-direction: column; justify-content: flex-end; position: relative; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
                    <div style="position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,0,0,0.8), rgba(0,0,0,0.2)); border-radius: 12px;"></div>
                    <div style="position: relative; z-index: 1;">
                        <span style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #818CF8;">{obj.badge_text}</span>
                        <h3 style="margin: 0.25rem 0; font-size: 1.25rem; font-weight: 800;">{obj.title}</h3>
                        <p style="margin: 0 0 0.75rem 0; font-size: 0.8rem; opacity: 0.9;">{obj.subtitle}</p>
                        <span style="background: #2563EB; color: white; padding: 0.35rem 0.75rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700; display: inline-block;">{obj.button_text}</span>
                    </div>
                </div>
            ''')
        return mark_safe('<span style="color: #64748B;">Upload a background image to view live preview card.</span>')
    banner_preview_display.short_description = "Live Preview"


@admin.register(CompanyMenuItem)
class CompanyMenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'circle_preview', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'url')

    def circle_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="height: 38px; width: 38px; border-radius: 50%; object-fit: cover; border: 2px solid #E2E8F0;">')
        return mark_safe('<span style="color: #94A3B8; font-size: 0.8rem;">No icon</span>')
    circle_preview.short_description = "Preview"


@admin.register(HomeOfferCard)
class HomeOfferCardAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'badge_text', 'price_badge', 'offer_thumbnail', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'subtitle')

    def offer_thumbnail(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="height: 40px; width: 60px; object-fit: cover; border-radius: 6px; border: 1px solid #CBD5E1;">')
        return mark_safe('<span style="color: #94A3B8; font-size: 0.8rem;">No image</span>')
    offer_thumbnail.short_description = "Image"


@admin.register(PartnerLogo)
class PartnerLogoAdmin(admin.ModelAdmin):
    list_display = ('name', 'logo_preview', 'url', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

    def logo_preview(self, obj):
        if obj.logo_image:
            return mark_safe(f'<img src="{obj.logo_image.url}" style="height: 30px; max-width: 100px; object-fit: contain;">')
        return mark_safe(f'<span style="font-weight: 700; color: #0F172A;">{obj.name}</span>')
    logo_preview.short_description = "Logo Preview"


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'photo_preview', 'linkedin_url', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'role')

    def photo_preview(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" style="height: 40px; width: 40px; border-radius: 50%; object-fit: cover; border: 2px solid #E2E8F0;">')
        return mark_safe('<span style="color: #94A3B8; font-size: 0.8rem;">No photo</span>')
    photo_preview.short_description = "Photo"


@admin.register(ValueProposition)
class ValuePropositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_display', 'bg_color_class', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')

    def icon_display(self, obj):
        return mark_safe(f'<i class="{obj.icon_class}" style="font-size: 1.25rem; color: #4F46E5;"></i> {obj.icon_class}')
    icon_display.short_description = "Icon"


@admin.register(NavbarItem)
class NavbarItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_preview', 'url', 'menu_type', 'sort_order', 'is_active')
    list_editable = ('sort_order', 'is_active', 'menu_type')
    list_filter = ('menu_type', 'is_active')
    search_fields = ('title', 'url')
    readonly_fields = ('icon_preview_large',)

    def icon_preview(self, obj):
        if obj.icon:
            return mark_safe(f'<img src="{obj.icon.url}" style="height: 30px; width: 30px; object-fit: contain; border-radius: 6px; background: #F1F5F9; padding: 3px; border: 1px solid #CBD5E1;">')
        return mark_safe('<span style="color: #94A3B8; font-size: 0.8rem;">No icon</span>')
    icon_preview.short_description = "Icon Preview"

    def icon_preview_large(self, obj):
        if obj.icon:
            return mark_safe(f'<img src="{obj.icon.url}" style="max-height: 80px; max-width: 120px; object-fit: contain; border-radius: 8px; background: #F8FAFC; padding: 6px; border: 1px solid #E2E8F0;">')
        return "Upload an icon to preview"
    icon_preview_large.short_description = "Current Icon Preview"


