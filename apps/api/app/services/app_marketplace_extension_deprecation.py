"""Extension Deprecation — manage the deprecation lifecycle for extensions.

Handles deprecation announcements, migration paths, sunset scheduling,
and notification of affected users with grace periods.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class DeprecationPhase(str, Enum):
    ANNOUNCED = "announced"
    GRACE_PERIOD = "grace_period"
    SUNSET = "sunset"
    REMOVED = "removed"


@dataclass
class DeprecationNotice:
    extension_id: str
    version: str  # deprecated version or "*" for all
    phase: DeprecationPhase
    announced_at: str
    sunset_date: str  # when it will stop working
    replacement_id: str = ""  # suggested replacement
    migration_guide: str = ""
    affected_orgs: list[str] = field(default_factory=list)
    notified_orgs: set[str] = field(default_factory=set)
    reason: str = ""


class DeprecationService:
    """Manages extension deprecation lifecycle."""

    def __init__(self):
        self._notices: dict[str, DeprecationNotice] = {}

    def announce(self, extension_id: str, version: str, sunset_date: str,
                 reason: str = "", replacement_id: str = "",
                 migration_guide: str = "", affected_orgs: list[str] | None = None) -> DeprecationNotice:
        """Announce a deprecation."""
        notice = DeprecationNotice(
            extension_id=extension_id, version=version,
            phase=DeprecationPhase.ANNOUNCED,
            announced_at=datetime.now(timezone.utc).isoformat(),
            sunset_date=sunset_date, reason=reason,
            replacement_id=replacement_id,
            migration_guide=migration_guide,
            affected_orgs=affected_orgs or [],
        )
        key = f"{extension_id}@{version}"
        self._notices[key] = notice
        return notice

    def advance_phase(self, extension_id: str, version: str) -> tuple[bool, str]:
        """Move to the next deprecation phase."""
        key = f"{extension_id}@{version}"
        notice = self._notices.get(key)
        if not notice:
            return False, "Notice not found"
        transitions = {
            DeprecationPhase.ANNOUNCED: DeprecationPhase.GRACE_PERIOD,
            DeprecationPhase.GRACE_PERIOD: DeprecationPhase.SUNSET,
            DeprecationPhase.SUNSET: DeprecationPhase.REMOVED,
        }
        next_phase = transitions.get(notice.phase)
        if not next_phase:
            return False, f"Cannot advance from {notice.phase.value}"
        notice.phase = next_phase
        return True, f"Advanced to {next_phase.value}"

    def notify_org(self, extension_id: str, version: str, org_id: str) -> bool:
        key = f"{extension_id}@{version}"
        notice = self._notices.get(key)
        if not notice:
            return False
        notice.notified_orgs.add(org_id)
        return True

    def get_notice(self, extension_id: str, version: str) -> DeprecationNotice | None:
        return self._notices.get(f"{extension_id}@{version}")

    def get_active_deprecations(self, extension_id: str | None = None) -> list[DeprecationNotice]:
        notices = list(self._notices.values())
        if extension_id:
            notices = [n for n in notices if n.extension_id == extension_id]
        return [n for n in notices if n.phase != DeprecationPhase.REMOVED]

    def get_unnotified_orgs(self, extension_id: str, version: str) -> list[str]:
        notice = self.get_notice(extension_id, version)
        if not notice:
            return []
        return [o for o in notice.affected_orgs if o not in notice.notified_orgs]

    def is_deprecated(self, extension_id: str, version: str = "*") -> bool:
        notice = self.get_notice(extension_id, version)
        return notice is not None and notice.phase != DeprecationPhase.REMOVED

    def get_migration_info(self, extension_id: str, version: str) -> dict | None:
        notice = self.get_notice(extension_id, version)
        if not notice:
            return None
        return {
            "extension_id": extension_id, "version": version,
            "replacement_id": notice.replacement_id,
            "migration_guide": notice.migration_guide,
            "sunset_date": notice.sunset_date,
            "phase": notice.phase.value,
        }
