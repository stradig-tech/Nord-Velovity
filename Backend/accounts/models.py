from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text="Customer profile picture or photo")
    
    ROLE_CHOICES = (
        ('CUSTOMER', 'Customer'), ('STAFF', 'Staff'), 
        ('MANAGER', 'Manager'), ('OWNER', 'Owner'), ('SUPERADMIN', 'Superadmin')
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='CUSTOMER')
    is_verified = models.BooleanField(default=False)
    mfa_enabled = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    @property
    def avatar_url(self):
        """Returns the profile picture URL if set on user or customer_profile."""
        for attr in ('avatar', 'profile_picture', 'profile_image'):
            val = getattr(self, attr, None)
            if val and hasattr(val, 'url'):
                try:
                    return val.url
                except Exception:
                    pass
        if hasattr(self, 'customer_profile'):
            for attr in ('avatar', 'profile_picture', 'profile_image'):
                val = getattr(self.customer_profile, attr, None)
                if val and hasattr(val, 'url'):
                    try:
                        return val.url
                    except Exception:
                        pass
        return None

    @property
    def initials(self):
        """Returns 1-2 character initials for avatar fallback (e.g. ST for Stradig)."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        if self.first_name:
            return self.first_name[:2].upper()
        if self.username and '@' not in self.username:
            return self.username[:2].upper()
        if self.email:
            return self.email[:2].upper()
        return "NV"

class CustomerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='customer_profile')
    nationality = models.CharField(max_length=100, blank=True, null=True)
    preferred_language = models.CharField(max_length=10, default='en')
    marketing_consent = models.BooleanField(default=False)
    consent_timestamp = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class StaffProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='staff_profile')
    department = models.CharField(max_length=100, blank=True, null=True)
    permissions_override = models.JSONField(default=dict, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
