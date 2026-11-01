"""Consumer API Webhook Delivery Window — restrict webhook deliveries to time windows."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryWindow:
    window_id: str
    webhook_id: str
    consumer_id: str
    start_hour: int  # 0-23
    end_hour: int    # 0-23
    days_of_week: list[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])  # Mon-Fri
    timezone: str = "UTC"
    enabled: bool = True

@dataclass
class WindowCheckResult:
    allowed: bool
    current_hour: int
    current_day: int
    reason: str

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookDeliveryWindow:
    def __init__(self) -> None:
        self._windows: dict[tuple[str, str, str], DeliveryWindow] = {}

    def set_window(self, installation_id: str, window: DeliveryWindow) -> DeliveryWindow:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not (0 <= window.start_hour <= 23) or not (0 <= window.end_hour <= 23):
            raise ValueError("Hours must be 0-23")
        if not all(0 <= d <= 6 for d in window.days_of_week):
            raise ValueError("Days must be 0-6")
        self._windows[(installation_id, window.consumer_id, window.webhook_id)] = window
        return window

    def check(self, installation_id: str, consumer_id: str, webhook_id: str, now: datetime) -> WindowCheckResult:
        key = (installation_id, consumer_id, webhook_id)
        window = self._windows.get(key)
        if not window or not window.enabled:
            return WindowCheckResult(allowed=True, current_hour=now.hour, current_day=now.weekday(), reason="no_window")
        hour = now.hour
        day = now.weekday()
        if day not in window.days_of_week:
            return WindowCheckResult(allowed=False, current_hour=hour, current_day=day, reason="outside_day")
        if window.start_hour <= window.end_hour:
            in_window = window.start_hour <= hour < window.end_hour
        else:  # overnight window e.g. 22-06
            in_window = hour >= window.start_hour or hour < window.end_hour
        if not in_window:
            return WindowCheckResult(allowed=False, current_hour=hour, current_day=day, reason="outside_hours")
        return WindowCheckResult(allowed=True, current_hour=hour, current_day=day, reason="within_window")

    def get_window(self, installation_id: str, consumer_id: str, webhook_id: str) -> DeliveryWindow | None:
        return self._windows.get((installation_id, consumer_id, webhook_id))

    def list_windows(self, installation_id: str, consumer_id: str) -> list[DeliveryWindow]:
        return [w for (inst, cid, _), w in self._windows.items() if inst == installation_id and cid == consumer_id]
