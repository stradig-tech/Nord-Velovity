from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('my-bookings/<str:booking_ref>/', views.booking_order_detail_view, name='booking_order_detail'),
    path('my-wishlist/', views.my_wishlist_view, name='my_wishlist'),
    path('payment-details/', views.payment_details_view, name='payment_details'),
    path('settings/', views.settings_view, name='settings'),
    path('api/wishlist/toggle/<int:tour_id>/', views.api_toggle_wishlist, name='api_toggle_wishlist'),
    
    # Password Reset
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('forgot-password/done/', views.forgot_password_done_view, name='forgot_password_done'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_confirm_view, name='reset_password_confirm'),
    path('reset-password/complete/', views.reset_password_complete_view, name='reset_password_complete'),
    
    # Social Auth & QA Demo Fast Access
    path('social/<str:provider>/', views.social_login_view, name='social_login'),
    path('social/<str:provider>/demo/', views.social_demo_login_view, name='social_demo_login'),
]
