from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<slug:tour_slug>/', views.booking_create_view, name='create'),
    path('summary/<str:booking_ref>/', views.booking_summary_view, name='summary'),
    path('success/', views.booking_success_view, name='success'),
]
