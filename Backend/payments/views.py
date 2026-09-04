import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from bookings.models import Booking
from bookings.services import BookingService
from notifications.services import NotificationService
from .models import PaymentIntent

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request, booking_id):
    """
    Creates a Stripe Checkout Session for a specific booking.
    Returns the session URL so the frontend can redirect the user to Stripe.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Do not process if already paid/confirmed
    if booking.status in ['CONFIRMED', 'COMPLETED']:
        return JsonResponse({'error': 'Booking is already paid and confirmed.'}, status=400)

    try:
        # Create a new Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': booking.currency.lower(),
                    'product_data': {
                        'name': f"NordVelocity: {booking.booking_ref}",
                        'description': f"{booking.get_booking_type_display()} Booking",
                    },
                    'unit_amount': int(booking.total_amount * 100), # amount in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            # Success and cancel URLs (frontend URLs, fallback to basic API endpoints for now)
            success_url=request.build_absolute_uri(f'/payments/success/?ref={booking.booking_ref}'),
            cancel_url=request.build_absolute_uri(f'/payments/cancel/?ref={booking.booking_ref}'),
            customer_email=booking.customer.email if booking.customer else None,
            metadata={
                'booking_id': booking.id,
                'booking_ref': booking.booking_ref
            }
        )

        # Record this attempt in our PaymentIntent model
        PaymentIntent.objects.create(
            booking=booking,
            stripe_payment_intent_id=session.id, # Using session ID initially, will update with real PI upon success
            amount=booking.total_amount,
            currency=booking.currency,
            status='PENDING'
        )

        return JsonResponse({'checkout_url': session.url})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def stripe_webhook(request):
    """
    Stripe webhook listener.
    Stripe will send an HTTP POST request here when a payment succeeds or fails.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
        
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Retrieve the booking ID from the metadata we passed earlier
        booking_ref = session['metadata'].get('booking_ref')
        if not booking_ref:
             return HttpResponse("Missing metadata", status=400)
             
        try:
            booking = Booking.objects.get(booking_ref=booking_ref)
            
            # Update PaymentIntent
            pi = PaymentIntent.objects.filter(booking=booking, status='PENDING').last()
            if pi:
                pi.stripe_payment_intent_id = session.get('payment_intent', session.get('id'))
                pi.status = 'SUCCEEDED'
                pi.raw_response = session
                pi.save()
            
            # Transition the Booking to CONFIRMED!
            # The BookingService will log the transition and we will hook in Email notifications soon.
            BookingService.transition_status(
                booking=booking, 
                new_status='CONFIRMED', 
                reason='Stripe checkout succeeded'
            )
            
            # Send the email notifications
            NotificationService.send_payment_success(booking)
            NotificationService.send_booking_confirmation(booking)
            
        except Booking.DoesNotExist:
            return HttpResponse("Booking not found", status=404)
            
    # Handle payment failures (optional)
    elif event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']
        booking_ref = session['metadata'].get('booking_ref')
        # Could mark PaymentIntent as FAILED and notify customer here...
        
    return HttpResponse(status=200)

def process_offline_payment(request, booking_id):
    """
    Handles Offline Payment (Pay on Arrival / Bank Wire Transfer).
    1. Validates booking existence.
    2. Sets payment_method to 'OFFLINE' or 'BANK_TRANSFER'.
    3. Sets payment_status to 'UNPAID'.
    4. Transitions booking status to 'CONFIRMED' with audit log.
    5. Dispatches customer email with offline instructions & bank details.
    6. Redirects to booking success page with reference.
    """
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        method_type = request.POST.get('offline_method', 'OFFLINE') # 'OFFLINE' or 'BANK_TRANSFER'
        notes = request.POST.get('customer_payment_notes', '').strip()

        booking.payment_method = method_type
        booking.payment_status = 'UNPAID'
        if notes:
            booking.customer_notes = f"{booking.customer_notes or ''}\n[Payment Note]: {notes}".strip()
        booking.save(update_fields=['payment_method', 'payment_status', 'customer_notes', 'updated_at'])

        # Transition status to CONFIRMED (reservation confirmed, payment due offline)
        BookingService.transition_status(
            booking=booking,
            new_status='CONFIRMED',
            changed_by=request.user if request.user.is_authenticated else booking.customer,
            reason=f"Offline payment selected: {booking.get_payment_method_display()}"
        )

        # Dispatch automated confirmation email with bank/cash details
        NotificationService.send_offline_payment_instructions(booking)

        from django.shortcuts import redirect
        return redirect(f"/bookings/success/?ref={booking.booking_ref}&method=offline")

    from django.shortcuts import redirect
    return redirect('bookings:summary', booking_ref=booking.booking_ref)


def payment_success(request):
    ref = request.GET.get('ref')
    from django.shortcuts import redirect
    return redirect(f"/bookings/success/?ref={ref}&method=stripe")

def payment_cancel(request):
    ref = request.GET.get('ref')
    from django.shortcuts import redirect
    return redirect(f"/bookings/summary/{ref}/?cancelled=1")


def paypal_create_order(request, booking_id):
    """
    API endpoint that creates a PayPal Order for the given booking.
    Returns JSON with order_id and approve_url.
    """
    from .paypal import PayPalService
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status in ['CONFIRMED', 'COMPLETED'] and booking.payment_status == 'PAID':
        return JsonResponse({'error': 'Booking is already paid.'}, status=400)

    res = PayPalService.create_order(booking)
    return JsonResponse(res)


def paypal_approve_order(request, booking_id):
    """
    Captures payment for an approved PayPal order and marks the booking as confirmed & paid.
    """
    from .paypal import PayPalService
    from django.shortcuts import redirect
    booking = get_object_or_404(Booking, id=booking_id)
    order_id = request.GET.get('order_id') or request.POST.get('order_id')

    if not order_id:
        return redirect(f"/bookings/summary/{booking.booking_ref}/?error=missing_paypal_order")

    capture_res = PayPalService.capture_order(order_id)
    if capture_res.get('success'):
        booking.payment_method = 'PAYPAL'
        booking.payment_status = 'PAID'
        booking.save(update_fields=['payment_method', 'payment_status', 'updated_at'])

        # Record payment intent
        PaymentIntent.objects.create(
            booking=booking,
            stripe_payment_intent_id=order_id,
            amount=booking.total_amount,
            currency=booking.currency,
            status='SUCCEEDED',
            payment_method_type='paypal',
            idempotency_key=f"paypal-{order_id}"
        )

        BookingService.transition_status(
            booking=booking,
            new_status='CONFIRMED',
            changed_by=request.user if request.user.is_authenticated else booking.customer,
            reason=f"PayPal payment captured successfully (Order: {order_id})"
        )

        NotificationService.send_payment_success(booking)
        NotificationService.send_booking_confirmation(booking)

        return redirect(f"/bookings/success/?ref={booking.booking_ref}&method=paypal")
    else:
        error_msg = capture_res.get('error', 'PayPal payment could not be captured.')
        return redirect(f"/bookings/summary/{booking.booking_ref}/?error={error_msg}")
