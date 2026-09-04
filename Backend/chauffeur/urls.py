from django.urls import path
from . import views

app_name = 'chauffeur'

urlpatterns = [
    path('', views.transport_home_view, name='hub'),
    path('home/', views.transport_home_view, name='home'),
    path('vehicles/', views.vehicle_list_view, name='list'),
    path('vehicles/<slug:slug>/', views.vehicle_detail_view, name='detail'),
    path('book/<slug:slug>/', views.chauffeur_booking_create_view, name='book'),
    path('api/calculate-fare/', views.api_calculate_chauffeur_fare, name='api_calculate_fare'),
]
