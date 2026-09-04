import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import NotificationTemplate, NotificationLog
from bookings.models import Booking

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service for sending email and SMS notifications.
    Adapted from Laravel's Event/Listener notification pattern.
    """

    @staticmethod
    def send_booking_confirmation(booking: Booking):
        """
        Sends an email when a booking is created/confirmed.
        """
        if not booking.customer or not booking.customer.email:
            return False

        subject = f"Booking Confirmation: {booking.booking_ref}"
        body = f"Hello {booking.customer.get_full_name()},\n\nYour booking {booking.booking_ref} is confirmed. Total: €{booking.total_amount}.\n\nThank you for choosing Nord Velocity."

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@nordvelocity.com',
                recipient_list=[booking.customer.email],
                fail_silently=False,
            )
            template, _ = NotificationTemplate.objects.get_or_create(
                slug='booking_confirmed',
                defaults={
                    'name': 'Booking Confirmation',
                    'subject_template': 'Booking Confirmation: {booking_ref}',
                    'body_text': body,
                    'body_html': body,
                    'channel': 'EMAIL'
                }
            )
            NotificationLog.objects.create(
                booking=booking,
                template=template,
                recipient_user=booking.customer,
                recipient_email=booking.customer.email,
                channel='EMAIL',
                status='SENT'
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send booking confirmation email for {booking.booking_ref}: {e}")
            return False

    @staticmethod
    def send_payment_success(booking: Booking):
        """
        Sends a payment receipt/success email.
        """
        if not booking.customer or not booking.customer.email:
            return False

        subject = f"Payment Received: {booking.booking_ref}"
        body = f"Hello {booking.customer.get_full_name()},\n\nWe have successfully received your payment of €{booking.total_amount} for booking {booking.booking_ref}.\n\nThank you!"

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email='noreply@nordvelocity.com',
                recipient_list=[booking.customer.email],
                fail_silently=False,
            )
            template, _ = NotificationTemplate.objects.get_or_create(
                slug='payment_receipt',
                defaults={
                    'name': 'Payment Receipt',
                    'subject_template': 'Payment Received: {booking_ref}',
                    'body_text': body,
                    'body_html': body,
                    'channel': 'EMAIL'
                }
            )
            NotificationLog.objects.create(
                booking=booking,
                template=template,
                recipient_user=booking.customer,
                recipient_email=booking.customer.email,
                channel='EMAIL',
                status='SENT'
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send payment email for {booking.booking_ref}: {e}")
            return False

    @staticmethod
    def send_offline_payment_instructions(booking: Booking):
        """
        Sends an email with offline payment instructions (Bank wire or Pay on Arrival).
        """
        if not booking.customer or not booking.customer.email:
            return False

        from core.models import SiteSetting
        settings_obj = SiteSetting.objects.first()
        bank_info = ""
        if settings_obj and settings_obj.bank_iban:
            bank_info = (
                f"\n\nBANK TRANSFER DETAILS:\n"
                f"Bank: {settings_obj.bank_name}\n"
                f"Account Name: {settings_obj.bank_account_name}\n"
                f"IBAN: {settings_obj.bank_iban}\n"
                f"SWIFT / BIC: {settings_obj.bank_swift_bic}\n"
                f"Reference Code: {booking.booking_ref}\n"
                f"Instructions: {settings_obj.offline_payment_instructions}\n"
            )

        subject = f"Booking Reserved (Offline Payment): {booking.booking_ref}"
        body = (
            f"Hello {booking.customer.get_full_name()},\n\n"
            f"Your booking {booking.booking_ref} has been successfully recorded!\n"
            f"Total Amount: €{booking.total_amount}\n"
            f"Payment Method: {booking.get_payment_method_display()}\n"
            f"Payment Status: Pending Collection upon arrival\n"
            f"{bank_info}\n"
            f"If paying on arrival, you may pay via cash (EUR) or card directly to your private chauffeur or concierge.\n\n"
            f"Warm regards,\nNord Velocity Concierge Team"
        )

        try:
            send_mail(
                subject=subject,
                message=body,
                from_email='noreply@nordvelocity.com',
                recipient_list=[booking.customer.email],
                fail_silently=False,
            )
            template, _ = NotificationTemplate.objects.get_or_create(
                slug='offline_payment_instructions',
                defaults={
                    'name': 'Offline Payment Instructions',
                    'subject_template': 'Booking Reserved (Offline Payment): {booking_ref}',
                    'body_text': body,
                    'body_html': body,
                    'channel': 'EMAIL'
                }
            )
            NotificationLog.objects.create(
                booking=booking,
                template=template,
                recipient_user=booking.customer,
                recipient_email=booking.customer.email,
                channel='EMAIL',
                status='SENT'
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send offline payment email for {booking.booking_ref}: {e}")
            return False

