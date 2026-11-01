"""App API Webhook Delivery Window — restrict delivery to time windows."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryWindow:
    window_id: str
    destination: str
    start_hour: int  # 0-23
    end_hour: int    # 0-23
    timezone: str = "UTC"
    enabled: bool = True

class AppAPIWebhookDeliveryWindow:
    def __init__(self) -> None:
        self._windows: dict[tuple[str, str], DeliveryWindow] = {}

    def configure(self, installation_id: str, window_id: str, destination: str, start_hour: int, end_hour: int, timezone: str = "UTC") -> DeliveryWindow:
        if not installation_id: raise ValueError("installation_id is required")
        if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23): raise ValueError("hours must be 0-23")
        w = DeliveryWindow(window_id=window_id, destination=destination, start_hour=start_hour, end_hour=end_hour, timezone=timezone)
        self._windows[(installation_id, window_id)] = w
        return w

    def is_in_window(self, installation_id: str, window_id: str, current_hour: int) -> bool:
        w = self._get(installation_id, window_id)
        if not w.enabled: return False
        if w.start_hour <= w.end_hour:
            return w.start_hour <= current_hour < w.end_hour
        return current_hour >= w.start_hour or current_hour < w.end_hour  # overnight

    def list_windows(self, installation_id: str) -> list[DeliveryWindow]:
        return [w for (inst, _), w in self._windows.items() if inst == installation_id]

    def _get(self, installation_id: str, window_id: str) -> DeliveryWindow:
        w = self._windows.get((installation_id, window_id))
        if w is None: raise KeyError(f"Window {window_id} not found")
        return w
