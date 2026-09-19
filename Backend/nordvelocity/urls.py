"""
URL configuration for nordvelocity project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from core.views import home_view, about_view, faq_view, contact_view
from django.views.generic import RedirectView

from bookings.views_admin import (
    departure_calendar_view,
    departure_calendar_api,
    departure_status_toggle_api,
    departure_capacity_update_api,
    admin_manual_booking_view,
    admin_rebook_departure_api
)

# Extend standard Django Admin site URLs
_orig_admin_get_urls = admin.site.get_urls

def _custom_admin_get_urls():
    custom_urls = [
        path('operations/calendar/', departure_calendar_view, name='departure_calendar'),
        path('bookings/manual-create/', admin_manual_booking_view, name='manual_booking_create'),
        path('api/departures/calendar/', departure_calendar_api, name='departure_calendar_api'),
        path('api/departures/<int:departure_id>/status/', departure_status_toggle_api, name='departure_status_api'),
        path('api/departures/<int:departure_id>/capacity/', departure_capacity_update_api, name='departure_capacity_api'),
        path('api/bookings/<int:booking_id>/rebook/', admin_rebook_departure_api, name='booking_rebook_api'),
    ]
    return custom_urls + _orig_admin_get_urls()

admin.site.get_urls = _custom_admin_get_urls

urlpatterns = [
    path('admin/operations/calendar/', departure_calendar_view, name='departure_calendar'),
    path('admin/bookings/manual-create/', admin_manual_booking_view, name='manual_booking_create'),
    path('admin/api/departures/calendar/', departure_calendar_api, name='departure_calendar_api'),
    path('admin/api/departures/<int:departure_id>/status/', departure_status_toggle_api, name='departure_status_api'),
    path('admin/api/departures/<int:departure_id>/capacity/', departure_capacity_update_api, name='departure_capacity_api'),
    path('admin/api/bookings/<int:booking_id>/rebook/', admin_rebook_departure_api, name='booking_rebook_api'),
    path('admin/', admin.site.urls),
    path('payments/', include('payments.urls')),
    path('tours/', include('tours.urls')),
    path('packages/', RedirectView.as_view(url='/tours/', permanent=True)),
    path('transport/', include('chauffeur.urls')),
    path('chauffeur/', RedirectView.as_view(url='/transport/', permanent=True)),
    path('cabs/', RedirectView.as_view(url='/transport/vehicles/', permanent=True)),
    path('accounts/', include('accounts.urls')),
    path('bookings/', include('bookings.urls')),
    path('login/', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('signup/', RedirectView.as_view(url='/accounts/signup/', permanent=False)),
    path('dashboard/', RedirectView.as_view(url='/accounts/dashboard/', permanent=False)),
    path('my-bookings/', RedirectView.as_view(url='/accounts/my-bookings/', permanent=False)),
    path('my-wishlist/', RedirectView.as_view(url='/accounts/my-wishlist/', permanent=False)),
    path('forgot-password/', RedirectView.as_view(url='/accounts/forgot-password/', permanent=False)),
    path('destination/', RedirectView.as_view(url='/tours/destinations/', permanent=True)),
    path('destinations/', RedirectView.as_view(url='/tours/destinations/', permanent=True)),
    path('about/', about_view, name='about'),
    path('faq/', faq_view, name='faq'),
    path('contact/', contact_view, name='contact'),
    path('blog/', include('content.urls')),
    path('custom-admin/', include('core.admin_urls')),
    path('', home_view, name='home'),
]

from django.views.static import serve
from django.urls import re_path

# Ensure media uploads (hero images, destination photos) are always served on cPanel
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += [
        re_path(r'^(?:.*/)?images/(?P<path>.*)$', serve, {'document_root': settings.STATICFILES_DIRS[0] / 'images'}),
        re_path(r'^style\.css$', serve, {'document_root': settings.STATICFILES_DIRS[0], 'path': 'style.css'}),
        re_path(r'^signin\.svg$', serve, {'document_root': settings.STATICFILES_DIRS[0], 'path': 'signin.svg'}),
    ]









