"""API Consumer Usage Heatmap — visualize API usage patterns by hour and day."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class HeatmapCell:
    day: str  # "mon"-"sun"
    hour: int  # 0-23
    request_count: int = 0
    error_count: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiUsageHeatmap:
    DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

    def __init__(self) -> None:
        self._data: dict[tuple[str, str, int], HeatmapCell] = {}

    def record(self, installation_id: str, day: str, hour: int, requests: int = 1, errors: int = 0) -> HeatmapCell:
        if not installation_id: raise ValueError("installation_id is required")
        if day not in self.DAYS: raise ValueError(f"Invalid day: {day}")
        if not 0 <= hour <= 23: raise ValueError("hour must be 0-23")
        key = (installation_id, day, hour)
        cell = self._data.get(key)
        if cell is None:
            cell = HeatmapCell(day=day, hour=hour)
            self._data[key] = cell
        cell.request_count += requests
        cell.error_count += errors
        return cell

    def get_heatmap(self, installation_id: str) -> list[HeatmapCell]:
        return [c for (inst, _, _), c in self._data.items() if inst == installation_id]

    def peak_hour(self, installation_id: str) -> tuple[str, int, int] | None:
        cells = self.get_heatmap(installation_id)
        if not cells: return None
        peak = max(cells, key=lambda c: c.request_count)
        return (peak.day, peak.hour, peak.request_count)

    def total_requests(self, installation_id: str) -> int:
        return sum(c.request_count for (inst, _, _), c in self._data.items() if inst == installation_id)
