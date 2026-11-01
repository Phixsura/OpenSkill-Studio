"""Platform Uptime Monitor — track uptime across all platform services.

Monitors service availability, calculates SLA compliance, tracks
downtime incidents, and provides uptime history.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class UptimeRecord:
    service: str
    total_checks: int = 0
    successful_checks: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_downtime: float = 0.0

    @property
    def uptime_pct(self) -> float:
        if not self.total_checks:
            return 100.0
        return round(self.successful_checks / self.total_checks * 100, 3)


class PlatformUptimeMonitorService:
    """Tracks uptime across platform services."""

    def __init__(self):
        self._records: dict[str, UptimeRecord] = {}

    def check(self, service: str, is_up: bool) -> UptimeRecord:
        if service not in self._records:
            self._records[service] = UptimeRecord(service=service)
        r = self._records[service]
        r.total_checks += 1
        if is_up:
            r.successful_checks += 1
            r.current_streak += 1
            r.longest_streak = max(r.longest_streak, r.current_streak)
        else:
            r.current_streak = 0
            r.last_downtime = time.time()
        return r

    def get_uptime(self, service: str) -> dict:
        r = self._records.get(service, UptimeRecord(service=service))
        return {
            "service": service, "uptime_pct": r.uptime_pct,
            "total_checks": r.total_checks, "current_streak": r.current_streak,
            "longest_streak": r.longest_streak,
            "sla_99": r.uptime_pct >= 99.0,
            "sla_999": r.uptime_pct >= 99.9,
            "sla_9999": r.uptime_pct >= 99.99,
        }

    def get_all(self) -> list[dict]:
        return [self.get_uptime(s) for s in sorted(self._records.keys())]

    def get_overall(self) -> dict:
        if not self._records:
            return {"overall_uptime": 100.0, "services": 0}
        uptimes = [r.uptime_pct for r in self._records.values()]
        return {
            "overall_uptime": round(sum(uptimes) / len(uptimes), 3),
            "services": len(self._records),
            "all_healthy": all(r.current_streak > 0 for r in self._records.values()),
        }
