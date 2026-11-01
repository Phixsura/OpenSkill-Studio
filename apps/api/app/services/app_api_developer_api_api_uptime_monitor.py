"""App API Developer API Uptime Monitor — track uptime windows and availability."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class UptimeWindow:
    start_at: float
    end_at: float
    status: str  # "up", "down", "degraded"

@dataclass
class UptimeRecord:
    endpoint: str
    windows: list[UptimeWindow] = field(default_factory=list)

    @property
    def uptime_pct(self) -> float:
        if not self.windows: return 100.0
        total = sum(w.end_at - w.start_at for w in self.windows)
        up = sum(w.end_at - w.start_at for w in self.windows if w.status == "up")
        return round(up / total * 100, 3) if total > 0 else 100.0

    @property
    def total_downtime_minutes(self) -> float:
        return round(sum((w.end_at - w.start_at) / 60 for w in self.windows if w.status == "down"), 1)

class AppAPIDeveloperAPIApiUptimeMonitor:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str], UptimeRecord] = {}

    def record_window(self, installation_id: str, endpoint: str, duration_seconds: float, status: str) -> UptimeRecord:
        if not installation_id: raise ValueError("installation_id is required")
        if status not in ("up", "down", "degraded"): raise ValueError("invalid status")
        if duration_seconds <= 0: raise ValueError("duration must be positive")
        key = (installation_id, endpoint)
        if key not in self._records:
            self._records[key] = UptimeRecord(endpoint=endpoint)
        r = self._records[key]
        now = time.time()
        r.windows.append(UptimeWindow(start_at=now - duration_seconds, end_at=now, status=status))
        return r

    def get_uptime(self, installation_id: str, endpoint: str) -> float:
        key = (installation_id, endpoint)
        r = self._records.get(key)
        return r.uptime_pct if r else 100.0

    def all_records(self, installation_id: str) -> list[UptimeRecord]:
        return [r for (inst, _), r in self._records.items() if inst == installation_id]

    def below_threshold(self, installation_id: str, threshold_pct: float = 99.9) -> list[UptimeRecord]:
        return [r for r in self.all_records(installation_id) if r.uptime_pct < threshold_pct]
