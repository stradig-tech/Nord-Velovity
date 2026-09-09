from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class AbstractChannelAdapter(ABC):
    """
    Standard interface for all external OTA distribution channels (e.g., GetYourGuide, Viator).
    Ensures unified inventory deduction and prevents channel fragmentation.
    """

    def __init__(self, channel):
        self.channel = channel

    @abstractmethod
    def push_availability(self, departure, vehicle_type, sellable_count: int) -> Dict[str, Any]:
        """
        Pushes the current sellable seat count to the OTA.
        Must return: {'success': bool, 'payload': dict, 'error': Optional[str]}
        """
        pass

    @abstractmethod
    def import_bookings(self, since_datetime: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Polls or imports new external reservations confirmed on the OTA platform.
        """
        pass

    @abstractmethod
    def sync_cancellation(self, external_reference: str) -> Dict[str, Any]:
        """
        Notifies OTA or handles an external cancellation.
        """
        pass
