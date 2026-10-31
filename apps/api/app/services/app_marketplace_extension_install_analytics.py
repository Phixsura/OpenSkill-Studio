"""Install Analytics — track extension installation patterns and trends.

Monitors install/uninstall events, retention rates, geographic distribution,
version adoption curves, and churn analysis.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class InstallAction(str, Enum):
    INSTALL = "install"
    UNINSTALL = "uninstall"
    UPDATE = "update"
    REINSTALL = "reinstall"


@dataclass
class InstallEvent:
    event_id: str
    extension_id: str
    user_id: str
    action: InstallAction
    version: str
    source: str = ""  # marketplace, cli, api, recommendation
    region: str = ""
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class InstallAnalyticsService:
    """Tracks installation patterns with retention and churn analysis."""

    def __init__(self):
        self._events: list[InstallEvent] = []
        self._active: dict[str, set[str]] = defaultdict(set)  # ext_id -> user_ids

    def track(self, extension_id: str, user_id: str, action: InstallAction,
              version: str = "", source: str = "", region: str = "") -> InstallEvent:
        event = InstallEvent(
            event_id=f"ie_{secrets.token_urlsafe(8)}",
            extension_id=extension_id, user_id=user_id,
            action=action, version=version, source=source, region=region,
        )
        self._events.append(event)

        if action in (InstallAction.INSTALL, InstallAction.REINSTALL):
            self._active[extension_id].add(user_id)
        elif action == InstallAction.UNINSTALL:
            self._active[extension_id].discard(user_id)

        return event

    def get_active_installs(self, extension_id: str) -> int:
        return len(self._active.get(extension_id, set()))

    def get_install_stats(self, extension_id: str) -> dict:
        events = [e for e in self._events if e.extension_id == extension_id]
        by_action: dict[str, int] = defaultdict(int)
        for e in events:
            by_action[e.action.value] += 1

        installs = by_action.get("install", 0) + by_action.get("reinstall", 0)
        uninstalls = by_action.get("uninstall", 0)
        retention = round((1 - uninstalls / max(installs, 1)) * 100, 1) if installs else 0

        return {
            "active_installs": self.get_active_installs(extension_id),
            "total_installs": installs,
            "total_uninstalls": uninstalls,
            "updates": by_action.get("update", 0),
            "retention_rate": retention,
        }

    def get_source_breakdown(self, extension_id: str) -> dict[str, int]:
        sources: dict[str, int] = defaultdict(int)
        for e in self._events:
            if e.extension_id == extension_id and e.action == InstallAction.INSTALL:
                sources[e.source or "unknown"] += 1
        return dict(sources)

    def get_region_breakdown(self, extension_id: str) -> dict[str, int]:
        regions: dict[str, int] = defaultdict(int)
        for e in self._events:
            if e.extension_id == extension_id and e.action == InstallAction.INSTALL:
                regions[e.region or "unknown"] += 1
        return dict(regions)

    def get_version_adoption(self, extension_id: str) -> dict[str, int]:
        # Track latest version per active user
        user_versions: dict[str, str] = {}
        for e in self._events:
            if e.extension_id == extension_id and e.version:
                if e.action in (InstallAction.INSTALL, InstallAction.UPDATE, InstallAction.REINSTALL):
                    user_versions[e.user_id] = e.version
                elif e.action == InstallAction.UNINSTALL:
                    user_versions.pop(e.user_id, None)
        adoption: dict[str, int] = defaultdict(int)
        for v in user_versions.values():
            adoption[v] += 1
        return dict(adoption)

    def get_churn_rate(self, extension_id: str) -> float:
        installs = sum(1 for e in self._events
                       if e.extension_id == extension_id
                       and e.action == InstallAction.INSTALL)
        uninstalls = sum(1 for e in self._events
                         if e.extension_id == extension_id
                         and e.action == InstallAction.UNINSTALL)
        return round(uninstalls / max(installs, 1) * 100, 1)
