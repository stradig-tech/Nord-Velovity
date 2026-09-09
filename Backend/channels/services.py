import logging
from typing import Dict, Any, Optional
from django.utils.module_loading import import_string
from django.utils import timezone
from .models import Channel, ChannelSyncLog
from tours.models import Departure, DepartureCapacity, VehicleType

logger = logging.getLogger(__name__)


class ChannelSyncService:
    """
    Orchestration service for pushing real-time inventory updates and logging synchronization events.
    Fulfills Guide Section ১২ (OTA-Ready) and Section ১৩ (Sync Failure Monitoring).
    """

    @staticmethod
    def get_adapter(channel: Channel):
        if not channel.adapter_class:
            return None
        try:
            adapter_cls = import_string(channel.adapter_class)
            return adapter_cls(channel)
        except Exception as e:
            logger.error("Failed to load adapter %s: %s", channel.adapter_class, e)
            return None

    @classmethod
    def push_departure_availability(cls, departure: Departure, vehicle_type: Optional[VehicleType] = None):
        """
        Pushes current sellable capacity for a departure to all active OTA channels.
        Writes an audit record to ChannelSyncLog for each channel.
        """
        active_channels = Channel.objects.filter(is_active=True)
        if not active_channels.exists():
            return

        capacities = departure.capacities.all()
        if vehicle_type:
            capacities = capacities.filter(vehicle_type=vehicle_type)

        for channel in active_channels:
            adapter = cls.get_adapter(channel)
            if not adapter:
                continue

            for cap in capacities:
                sellable = cap.public_sellable
                try:
                    result = adapter.push_availability(
                        departure=departure,
                        vehicle_type=cap.vehicle_type,
                        sellable_count=sellable
                    )
                    success = result.get('success', False)
                    status_str = 'SUCCESS' if success else 'FAILED'

                    ChannelSyncLog.objects.create(
                        channel=channel,
                        action='AVAILABILITY_PUSH',
                        status=status_str,
                        departure=departure,
                        request_payload=result.get('payload', {}),
                        response_payload=result.get('response', {}),
                        error_message=result.get('error', ''),
                        requires_attention=not success
                    )
                    channel.last_sync_at = timezone.now()
                    channel.last_sync_status = status_str
                    channel.save(update_fields=['last_sync_at', 'last_sync_status'])

                except Exception as e:
                    logger.exception("Error syncing availability to %s: %s", channel.name, e)
                    ChannelSyncLog.objects.create(
                        channel=channel,
                        action='AVAILABILITY_PUSH',
                        status='FAILED',
                        departure=departure,
                        error_message=str(e),
                        requires_attention=True
                    )
                    channel.last_sync_status = 'FAILED'
                    channel.save(update_fields=['last_sync_status'])

    @classmethod
    def retry_failed_syncs(cls) -> int:
        """
        Retries all failed sync attempts that require attention.
        """
        failed_logs = ChannelSyncLog.objects.filter(status='FAILED', requires_attention=True)
        retried_count = 0
        for log in failed_logs:
            if log.departure:
                cls.push_departure_availability(log.departure)
                log.retry_count += 1
                log.requires_attention = False
                log.resolved_at = timezone.now()
                log.save(update_fields=['retry_count', 'requires_attention', 'resolved_at'])
                retried_count += 1
        return retried_count
