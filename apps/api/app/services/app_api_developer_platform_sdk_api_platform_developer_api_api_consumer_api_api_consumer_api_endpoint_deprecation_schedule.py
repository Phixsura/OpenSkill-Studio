"""Endpoint Deprecation Schedule — manage endpoint sunset timelines."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class DeprecationEntry:
    endpoint_id: str
    path: str
    deprecated_at: datetime
    sunset_at: datetime
    replacement_path: str | None = None
    migration_guide_url: str | None = None
    status: str = "active"  # "active", "deprecated", "sunset"

    def effective_status(self, now: datetime) -> str:
        if now >= self.sunset_at:
            return "sunset"
        if now >= self.deprecated_at:
            return "deprecated"
        return "active"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointDeprecationSchedule:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], DeprecationEntry] = {}

    def schedule(self, installation_id: str, entry: DeprecationEntry) -> DeprecationEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if entry.sunset_at <= entry.deprecated_at:
            raise ValueError("sunset_at must be after deprecated_at")
        key = (installation_id, entry.endpoint_id)
        self._entries[key] = entry
        log.info("deprecation_scheduled", installation_id=installation_id, endpoint=entry.path, sunset=entry.sunset_at.isoformat())
        return entry

    def get(self, installation_id: str, endpoint_id: str) -> DeprecationEntry | None:
        return self._entries.get((installation_id, endpoint_id))

    def list_deprecated(self, installation_id: str, now: datetime) -> list[DeprecationEntry]:
        return [e for (inst, _), e in self._entries.items() if inst == installation_id and e.effective_status(now) == "deprecated"]

    def list_sunset(self, installation_id: str, now: datetime) -> list[DeprecationEntry]:
        return [e for (inst, _), e in self._entries.items() if inst == installation_id and e.effective_status(now) == "sunset"]

    def upcoming(self, installation_id: str, now: datetime, within_days: int = 30) -> list[DeprecationEntry]:
        from datetime import timedelta
        cutoff = now + timedelta(days=within_days)
        return [e for (inst, _), e in self._entries.items()
                if inst == installation_id and e.effective_status(now) == "active" and e.deprecated_at <= cutoff]

    def list_all(self, installation_id: str) -> list[DeprecationEntry]:
        return [e for (inst, _), e in self._entries.items() if inst == installation_id]
