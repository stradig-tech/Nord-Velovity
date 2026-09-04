from django.urls import path
from . import views

app_name = 'tours'

urlpatterns = [
    path('', views.tour_list_view, name='list'),
    path('country/<slug:slug>/', views.country_detail_view, name='country_detail'),
    path('destinations/', views.destination_list_view, name='destination_list'),
    path('destinations/<slug:slug>/', views.destination_detail_view, name='destination_detail'),
    path('<slug:slug>/', views.tour_detail_view, name='detail'),
    path('api/<int:tour_id>/calculate-price/', views.api_calculate_tour_price, name='api_calculate_price'),
    path('api/<int:tour_id>/enquiry/', views.api_submit_enquiry, name='api_enquiry'),
]
