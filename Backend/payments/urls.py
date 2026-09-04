from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:booking_id>/', views.create_checkout_session, name='checkout'),
    path('offline/<int:booking_id>/', views.process_offline_payment, name='offline'),
    path('paypal/create/<int:booking_id>/', views.paypal_create_order, name='paypal_create'),
    path('paypal/approve/<int:booking_id>/', views.paypal_approve_order, name='paypal_approve'),
    path('webhook/', views.stripe_webhook, name='webhook'),
    path('success/', views.payment_success, name='success'),
    path('cancel/', views.payment_cancel, name='cancel'),
]
