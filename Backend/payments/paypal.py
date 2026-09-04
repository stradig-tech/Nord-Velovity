import requests
import base64
import logging
from django.conf import settings
from decimal import Decimal

logger = logging.getLogger(__name__)

class PayPalService:
    """
    Integrates with PayPal Orders API v2 for server-side order creation and capture.
    Supports sandbox and production modes.
    """

    @classmethod
    def get_base_url(cls) -> str:
        if getattr(settings, 'PAYPAL_MODE', 'sandbox') == 'live':
            return 'https://api-m.paypal.com'
        return 'https://api-m.sandbox.paypal.com'

    @classmethod
    def get_access_token(cls) -> str:
        client_id = getattr(settings, 'PAYPAL_CLIENT_ID', 'sb')
        secret = getattr(settings, 'PAYPAL_SECRET', 'sandbox_secret_placeholder')

        if client_id == 'sb' or 'placeholder' in secret:
            # Mock token for test environments
            return "mock_sandbox_access_token"

        url = f"{cls.get_base_url()}/v1/oauth2/token"
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        data = {'grant_type': 'client_credentials'}
        
        try:
            res = requests.post(url, auth=(client_id, secret), data=data, headers=headers, timeout=10)
            if res.status_code == 200:
                return res.json().get('access_token')
            logger.error(f"Failed to fetch PayPal access token: {res.text}")
            return None
        except Exception as e:
            logger.error(f"Error connecting to PayPal: {e}")
            return None

    @classmethod
    def create_order(cls, booking) -> dict:
        """
        Creates a PayPal checkout order for the given booking.
        """
        client_id = getattr(settings, 'PAYPAL_CLIENT_ID', 'sb')
        secret = getattr(settings, 'PAYPAL_SECRET', 'sandbox_secret_placeholder')

        # If running with mock sandbox credentials, provide simulated order ID
        if client_id == 'sb' or 'placeholder' in secret:
            import uuid
            mock_order_id = f"MOCK-PAYPAL-{uuid.uuid4().hex[:10].upper()}"
            return {
                "success": True,
                "order_id": mock_order_id,
                "approve_url": f"/payments/paypal/approve/{booking.id}/?order_id={mock_order_id}"
            }

        token = cls.get_access_token()
        if not token:
            return {"success": False, "error": "Unable to authenticate with PayPal"}

        url = f"{cls.get_base_url()}/v2/checkout/orders"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": booking.booking_ref,
                    "description": f"Nord Velocity Reservation {booking.booking_ref}",
                    "amount": {
                        "currency_code": booking.currency or "EUR",
                        "value": f"{booking.total_amount:.2f}"
                    }
                }
            ],
            "application_context": {
                "brand_name": "Nord Velocity Luxury Travel",
                "landing_page": "NO_PREFERENCE",
                "user_action": "PAY_NOW",
                "return_url": f"/payments/paypal/return/?booking_id={booking.id}",
                "cancel_url": f"/bookings/summary/{booking.booking_ref}/?cancelled=1"
            }
        }

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            data = res.json()
            if res.status_code in [200, 201]:
                order_id = data.get('id')
                approve_url = None
                for link in data.get('links', []):
                    if link.get('rel') == 'approve':
                        approve_url = link.get('href')
                        break
                return {
                    "success": True,
                    "order_id": order_id,
                    "approve_url": approve_url
                }
            else:
                logger.error(f"PayPal create order error: {data}")
                return {"success": False, "error": data.get('message', 'Failed to create PayPal order')}
        except Exception as e:
            logger.error(f"PayPal request exception: {e}")
            return {"success": False, "error": str(e)}

    @classmethod
    def capture_order(cls, order_id: str) -> dict:
        """
        Captures funds for an approved PayPal order.
        """
        client_id = getattr(settings, 'PAYPAL_CLIENT_ID', 'sb')
        secret = getattr(settings, 'PAYPAL_SECRET', 'sandbox_secret_placeholder')

        # Mock capture for test mode
        if order_id.startswith('MOCK-PAYPAL-') or client_id == 'sb' or 'placeholder' in secret:
            return {
                "success": True,
                "status": "COMPLETED",
                "capture_id": f"CAP-{order_id}"
            }

        token = cls.get_access_token()
        if not token:
            return {"success": False, "error": "Unable to authenticate with PayPal"}

        url = f"{cls.get_base_url()}/v2/checkout/orders/{order_id}/capture"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        try:
            res = requests.post(url, headers=headers, timeout=10)
            data = res.json()
            if res.status_code in [200, 201] and data.get('status') == 'COMPLETED':
                return {
                    "success": True,
                    "status": "COMPLETED",
                    "data": data
                }
            return {
                "success": False,
                "status": data.get('status'),
                "error": data.get('message', 'PayPal capture failed')
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
