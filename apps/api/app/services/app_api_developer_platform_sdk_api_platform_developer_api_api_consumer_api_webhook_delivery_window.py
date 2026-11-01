"""API Consumer Webhook Delivery Window — schedule delivery windows per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryWindow:
    consumer_id: str
    start_hour: int  # 0-23
    end_hour: int  # 0-23
    timezone: str = "UTC"
    days: list[str] = field(default_factory=lambda: ["mon", "tue", "wed", "thu", "fri", "sat", "sun"])
    buffer_outside_window: bool = True

VALID_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookDeliveryWindow:
    def __init__(self) -> None:
        self._windows: dict[tuple[str, str], DeliveryWindow] = {}

    def set_window(self, installation_id: str, window: DeliveryWindow) -> DeliveryWindow:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0 <= window.start_hour <= 23: raise ValueError("start_hour must be 0-23")
        if not 0 <= window.end_hour <= 23: raise ValueError("end_hour must be 0-23")
        invalid_days = set(window.days) - VALID_DAYS
        if invalid_days: raise ValueError(f"Invalid days: {invalid_days}")
        self._windows[(installation_id, window.consumer_id)] = window
        return window

    def is_in_window(self, installation_id: str, consumer_id: str, current_hour: int, current_day: str) -> bool:
        window = self._windows.get((installation_id, consumer_id))
        if window is None: return True  # no window = always deliver
        if current_day not in window.days: return False
        if window.start_hour <= window.end_hour:
            return window.start_hour <= current_hour < window.end_hour
        else:  # wraps midnight
            return current_hour >= window.start_hour or current_hour < window.end_hour

    def should_buffer(self, installation_id: str, consumer_id: str) -> bool:
        window = self._windows.get((installation_id, consumer_id))
        return window is not None and window.buffer_outside_window

    def list_windows(self, installation_id: str) -> list[DeliveryWindow]:
        return [w for (inst, _), w in self._windows.items() if inst == installation_id]
