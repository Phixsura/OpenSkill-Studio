"""App API CORS Origin Log — track cross-origin request origins.

Manages CORS origin logging:
- Log origins making cross-origin requests
- Track allowed vs blocked origins
- Origin frequency stats
- Per-installation scoped logs
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class OriginRecord:
    """A tracked CORS origin."""

    origin: str
    request_count: int = 0
    allowed_count: int = 0
    blocked_count: int = 0

    @property
    def block_rate(self) -> float:
        if self.request_count == 0:
            return 0.0
        return round(self.blocked_count / self.request_count * 100, 1)


class AppAPICORSOriginLog:
    """Track cross-origin request origins."""

    def __init__(self) -> None:
        self._origins: dict[tuple[str, str], OriginRecord] = {}

    def record(
        self, installation_id: str, origin: str, allowed: bool,
    ) -> OriginRecord:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not origin:
            raise ValueError("origin is required")

        key = (installation_id, origin)
        if key not in self._origins:
            self._origins[key] = OriginRecord(origin=origin)

        rec = self._origins[key]
        rec.request_count += 1
        if allowed:
            rec.allowed_count += 1
        else:
            rec.blocked_count += 1
        return rec

    def top_origins(self, installation_id: str, limit: int = 10) -> list[OriginRecord]:
        origins = [r for (inst, _), r in self._origins.items() if inst == installation_id]
        return sorted(origins, key=lambda r: r.request_count, reverse=True)[:limit]

    def blocked_origins(self, installation_id: str) -> list[OriginRecord]:
        return [r for (inst, _), r in self._origins.items() if inst == installation_id and r.blocked_count > 0]

    def unique_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._origins if inst == installation_id)
