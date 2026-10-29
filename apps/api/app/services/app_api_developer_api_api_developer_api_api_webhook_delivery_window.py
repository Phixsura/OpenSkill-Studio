"""App API Developer Webhook Delivery Window — restrict delivery to time windows."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryWindow:
    window_id: str
    destination: str
    start_hour: int  # 0-23 UTC
    end_hour: int    # 0-23 UTC
    days: list[int] = field(default_factory=lambda: list(range(7)))  # 0=Mon
    queued_count: int = 0
    delivered_count: int = 0

class AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryWindow:
    def __init__(self) -> None:
        self._windows: dict[tuple[str, str], DeliveryWindow] = {}

    def configure(self, installation_id: str, window_id: str, destination: str, start_hour: int, end_hour: int, days: list[int] | None = None) -> DeliveryWindow:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0 <= start_hour <= 23 or not 0 <= end_hour <= 23: raise ValueError("hours must be 0-23")
        if days:
            for d in days:
                if not 0 <= d <= 6: raise ValueError("days must be 0-6")
        key = (installation_id, window_id)
        w = DeliveryWindow(window_id=window_id, destination=destination, start_hour=start_hour, end_hour=end_hour, days=days or list(range(7)))
        self._windows[key] = w
        return w

    def can_deliver(self, installation_id: str, window_id: str, current_hour: int, current_day: int) -> bool:
        key = (installation_id, window_id)
        w = self._windows.get(key)
        if w is None: return True  # no window = always deliver
        if current_day not in w.days: return False
        if w.start_hour <= w.end_hour:
            return w.start_hour <= current_hour < w.end_hour
        # overnight window (e.g. 22-6)
        return current_hour >= w.start_hour or current_hour < w.end_hour

    def queue_event(self, installation_id: str, window_id: str) -> DeliveryWindow:
        key = (installation_id, window_id)
        w = self._windows.get(key)
        if w is None: raise KeyError(f"Window {window_id} not found")
        w.queued_count += 1
        return w

    def all_windows(self, installation_id: str) -> list[DeliveryWindow]:
        return [w for (inst, _), w in self._windows.items() if inst == installation_id]
