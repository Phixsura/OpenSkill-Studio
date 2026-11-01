"""API Deprecation Tracker — manage endpoint lifecycle from active to sunset.

Tracks deprecated API endpoints and their usage to plan safe removal:
- Register deprecation notices with sunset dates
- Track usage of deprecated endpoints per client
- Sunset enforcement: warn → block after sunset date
- Migration status tracking per consumer
- Deprecation report for platform operators
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()


class DeprecationPhase(str, Enum):
    ACTIVE = "active"         # not deprecated
    DEPRECATED = "deprecated" # deprecated, still serving
    SUNSET = "sunset"         # past sunset date, may block
    REMOVED = "removed"       # gone


class EnforcementAction(str, Enum):
    ALLOW = "allow"
    WARN = "warn"       # add deprecation headers
    BLOCK = "block"     # return 410 Gone


@dataclass
class DeprecationNotice:
    """A deprecation notice for an endpoint."""

    endpoint_key: str       # "GET /api/v1/old-endpoint"
    deprecated_at: datetime
    sunset_at: datetime     # when it will stop working
    replacement: str | None = None  # new endpoint
    message: str = ""
    phase: DeprecationPhase = DeprecationPhase.DEPRECATED
    block_after_sunset: bool = True


@dataclass
class UsageRecord:
    """Usage tracking for a deprecated endpoint."""

    endpoint_key: str
    client_id: str
    last_called_at: datetime
    call_count: int = 0
    warned: bool = False


@dataclass
class CheckResult:
    """Result of checking a request against deprecation rules."""

    action: EnforcementAction
    notice: DeprecationNotice | None = None
    headers: dict[str, str] = field(default_factory=dict)


@dataclass
class DeprecationReport:
    """Summary report for operators."""

    total_deprecated: int
    total_sunset: int
    total_active_consumers: int
    endpoints: list[dict]


class ApiDeprecationTracker:
    """Track and enforce API endpoint deprecations."""

    def __init__(self):
        self._notices: dict[str, DeprecationNotice] = {}
        # (endpoint_key, client_id) → UsageRecord
        self._usage: dict[tuple[str, str], UsageRecord] = defaultdict(
            lambda: UsageRecord("", "", datetime.now(UTC))
        )

    def deprecate(self, endpoint_key: str, sunset_at: datetime,
                  replacement: str | None = None, message: str = "",
                  block_after_sunset: bool = True) -> DeprecationNotice:
        """Register a deprecation notice."""
        notice = DeprecationNotice(
            endpoint_key=endpoint_key,
            deprecated_at=datetime.now(UTC),
            sunset_at=sunset_at,
            replacement=replacement,
            message=message,
            block_after_sunset=block_after_sunset,
        )
        self._notices[endpoint_key] = notice
        log.info("api.deprecated", endpoint=endpoint_key, sunset=sunset_at.isoformat())
        return notice

    def remove(self, endpoint_key: str) -> None:
        """Mark an endpoint as removed."""
        notice = self._notices.get(endpoint_key)
        if notice:
            notice.phase = DeprecationPhase.REMOVED

    def check(self, endpoint_key: str, client_id: str,
              now: datetime | None = None) -> CheckResult:
        """Check if a request to a deprecated endpoint should proceed.

        Returns the enforcement action and any headers to add.
        """
        now = now or datetime.now(UTC)
        notice = self._notices.get(endpoint_key)

        if notice is None:
            return CheckResult(action=EnforcementAction.ALLOW)

        # Update phase based on time
        if notice.phase != DeprecationPhase.REMOVED:
            if now >= notice.sunset_at:
                notice.phase = DeprecationPhase.SUNSET
            else:
                notice.phase = DeprecationPhase.DEPRECATED

        # Track usage
        key = (endpoint_key, client_id)
        usage = self._usage[key]
        usage.endpoint_key = endpoint_key
        usage.client_id = client_id
        usage.last_called_at = now
        usage.call_count += 1

        # Build deprecation headers
        headers: dict[str, str] = {}

        if notice.phase == DeprecationPhase.REMOVED:
            return CheckResult(
                action=EnforcementAction.BLOCK,
                notice=notice,
                headers={"Sunset": notice.sunset_at.strftime("%a, %d %b %Y %H:%M:%S GMT")},
            )

        if notice.phase == DeprecationPhase.SUNSET:
            if notice.block_after_sunset:
                headers["Sunset"] = notice.sunset_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
                if notice.replacement:
                    headers["Link"] = f'<{notice.replacement}>; rel="successor-version"'
                return CheckResult(
                    action=EnforcementAction.BLOCK,
                    notice=notice,
                    headers=headers,
                )

        # Deprecated but still serving — add warning headers
        headers["Deprecation"] = notice.deprecated_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
        headers["Sunset"] = notice.sunset_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
        if notice.replacement:
            headers["Link"] = f'<{notice.replacement}>; rel="successor-version"'
        usage.warned = True

        return CheckResult(
            action=EnforcementAction.WARN,
            notice=notice,
            headers=headers,
        )

    def get_consumers(self, endpoint_key: str) -> list[UsageRecord]:
        """Get all clients still using a deprecated endpoint."""
        return sorted(
            [u for (ek, _), u in self._usage.items() if ek == endpoint_key and u.call_count > 0],
            key=lambda u: u.call_count, reverse=True,
        )

    def get_consumer_count(self, endpoint_key: str) -> int:
        return len(self.get_consumers(endpoint_key))

    def get_report(self, now: datetime | None = None) -> DeprecationReport:
        """Generate a deprecation report for operators."""
        now = now or datetime.now(UTC)
        deprecated = [n for n in self._notices.values()
                      if n.phase == DeprecationPhase.DEPRECATED]
        sunset = [n for n in self._notices.values()
                  if n.phase in (DeprecationPhase.SUNSET, DeprecationPhase.REMOVED)]
        active_consumers = len({(ek, cid) for (ek, cid), u in self._usage.items()
                                if u.call_count > 0})

        endpoints = []
        for notice in sorted(self._notices.values(), key=lambda n: n.sunset_at):
            consumers = self.get_consumers(notice.endpoint_key)
            endpoints.append({
                "endpoint": notice.endpoint_key,
                "phase": notice.phase.value,
                "sunset_at": notice.sunset_at.isoformat(),
                "replacement": notice.replacement,
                "consumer_count": len(consumers),
                "total_calls": sum(c.call_count for c in consumers),
                "days_until_sunset": max(0, (notice.sunset_at - now).days),
            })

        return DeprecationReport(
            total_deprecated=len(deprecated),
            total_sunset=len(sunset),
            total_active_consumers=active_consumers,
            endpoints=endpoints,
        )

    def list_notices(self, phase: DeprecationPhase | None = None) -> list[DeprecationNotice]:
        notices = list(self._notices.values())
        if phase:
            notices = [n for n in notices if n.phase == phase]
        return sorted(notices, key=lambda n: n.sunset_at)
