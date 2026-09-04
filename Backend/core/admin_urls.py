from django.urls import path
from . import admin_views

app_name = 'custom_admin'

urlpatterns = [
    path('', admin_views.admin_dashboard_view, name='dashboard'),
    path('bookings/', admin_views.admin_bookings_view, name='bookings'),
    path('bookings/<str:booking_ref>/', admin_views.admin_booking_detail_view, name='booking_detail'),
    path('guests/', admin_views.admin_guests_view, name='guests'),
    path('guests/<int:guest_id>/', admin_views.admin_guest_detail_view, name='guest_detail'),
    path('reviews/', admin_views.admin_reviews_view, name='reviews'),
    path('earnings/', admin_views.admin_earnings_view, name='earnings'),
    path('settings/', admin_views.admin_settings_view, name='settings'),
]
