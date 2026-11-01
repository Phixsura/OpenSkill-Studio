"""App API Developer Endpoint Deprecation Warning — warn consumers of deprecated endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class DeprecationWarning:
    endpoint: str
    method: str
    replacement: str
    sunset_date: str  # ISO date string
    warning_header: str = ""
    consumers_warned: set[str] = field(default_factory=set)
    total_warnings_sent: int = 0

class AppAPIDeveloperAPIApiEndpointDeprecationWarning:
    def __init__(self) -> None:
        self._warnings: dict[tuple[str, str, str], DeprecationWarning] = {}

    def register(self, installation_id: str, endpoint: str, method: str, replacement: str, sunset_date: str) -> DeprecationWarning:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), endpoint)
        header = f'299 - "Deprecated API: use {replacement} instead. Sunset: {sunset_date}"'
        w = DeprecationWarning(endpoint=endpoint, method=method.upper(), replacement=replacement, sunset_date=sunset_date, warning_header=header)
        self._warnings[key] = w
        return w

    def check(self, installation_id: str, endpoint: str, method: str, consumer_id: str) -> DeprecationWarning | None:
        key = (installation_id, method.upper(), endpoint)
        w = self._warnings.get(key)
        if w is None: return None
        w.consumers_warned.add(consumer_id)
        w.total_warnings_sent += 1
        return w

    def all_warnings(self, installation_id: str) -> list[DeprecationWarning]:
        return [w for (inst, _, _), w in self._warnings.items() if inst == installation_id]

    def most_used_deprecated(self, installation_id: str, limit: int = 5) -> list[DeprecationWarning]:
        warnings = self.all_warnings(installation_id)
        return sorted(warnings, key=lambda w: w.total_warnings_sent, reverse=True)[:limit]
