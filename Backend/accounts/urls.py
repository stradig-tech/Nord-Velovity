from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('my-wishlist/', views.my_wishlist_view, name='my_wishlist'),
    path('settings/', views.settings_view, name='settings'),
    path('api/wishlist/toggle/<int:tour_id>/', views.api_toggle_wishlist, name='api_toggle_wishlist'),
]
