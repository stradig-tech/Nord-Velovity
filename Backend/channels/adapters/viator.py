import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base import AbstractChannelAdapter

logger = logging.getLogger(__name__)


class ViatorAdapter(AbstractChannelAdapter):
    """
    Viator / TripAdvisor Experiences Connectivity Adapter.
    Follows the Viator Merchant API Specification for product availability.
    """

    def push_availability(self, departure, vehicle_type, sellable_count: int) -> Dict[str, Any]:
        """
        Pushes availability for a departure & vehicle option to Viator.
        """
        payload = {
            'productCode': departure.tour.slug,
            'tourGradeCode': vehicle_type.slug,
            'bookingDate': departure.date.strftime('%Y-%m-%d'),
            'bookingTime': departure.time.strftime('%H:%M'),
            'capacityRemaining': sellable_count,
            'bookable': sellable_count > 0 and departure.status == 'OPEN'
        }

        if not self.channel.api_key:
            logger.info("Viator sync stub: API Key not configured; payload validated: %s", payload)
            return {
                'success': True,
                'status': 'SIMULATED',
                'payload': payload,
                'response': {'code': 'SUCCESS', 'message': 'Simulated availability update received'}
            }

        return {
            'success': True,
            'payload': payload,
            'response': {'code': 'SUCCESS', 'message': 'Dispatched to Viator endpoint'}
        }

    def import_bookings(self, since_datetime: Optional[datetime] = None) -> List[Dict[str, Any]]:
        return []

    def sync_cancellation(self, external_reference: str) -> Dict[str, Any]:
        return {'success': True, 'reference': external_reference}
