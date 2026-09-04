from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from .models import CustomUser, CustomerProfile, StaffProfile

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('avatar_thumbnail', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_verified')
    list_filter = ('role', 'is_active', 'is_verified')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('avatar_preview',)
    # Remove 'username' requirement and use email
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('avatar_preview', 'avatar', 'first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_verified', 'mfa_enabled', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def avatar_thumbnail(self, obj):
        if obj.avatar_url:
            return mark_safe(f'<img src="{obj.avatar_url}" style="height:36px; width:36px; border-radius:50%; object-fit:cover; border:1.5px solid #CBD5E1;">')
        return mark_safe(f'<div style="width:36px; height:36px; border-radius:50%; background:#4F46E5; color:white; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.8rem;">{obj.initials}</div>')
    avatar_thumbnail.short_description = "Avatar"

    def avatar_preview(self, obj):
        if obj.avatar_url:
            return mark_safe(f'<img src="{obj.avatar_url}" style="height:80px; width:80px; border-radius:50%; object-fit:cover; border:2px solid #4F46E5; box-shadow:0 2px 8px rgba(0,0,0,0.1);">')
        return mark_safe('<span style="color:#94A3B8; font-size:0.85rem;">No profile picture set</span>')
    avatar_preview.short_description = "Current Avatar"
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nationality', 'marketing_consent')
    search_fields = ('user__email', 'nationality')

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department')
    search_fields = ('user__email', 'department')
