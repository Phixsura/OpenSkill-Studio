"""Quick Launch — one-click extension deployment from templates.

Combines scaffold + configure + deploy into a single quick-launch
flow with preset configurations and instant preview.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum


class LaunchStatus(str, Enum):
    INITIALIZING = "initializing"
    CONFIGURING = "configuring"
    DEPLOYING = "deploying"
    LIVE = "live"
    FAILED = "failed"


@dataclass
class QuickLaunch:
    launch_id: str
    template_name: str
    extension_name: str
    runtime: str
    status: LaunchStatus = LaunchStatus.INITIALIZING
    preview_url: str = ""
    steps_completed: int = 0
    total_steps: int = 4
    error: str = ""
    started_at: float = 0.0

    def __post_init__(self):
        if not self.started_at:
            self.started_at = time.time()

    @property
    def progress_pct(self) -> int:
        return int(self.steps_completed / self.total_steps * 100)


class ExtensionQuickLaunchService:
    """One-click extension deployment."""

    def __init__(self):
        self._launches: dict[str, QuickLaunch] = {}

    def launch(self, template_name: str, extension_name: str,
               runtime: str = "node20") -> QuickLaunch:
        launch_id = f"ql_{secrets.token_urlsafe(8)}"
        ql = QuickLaunch(
            launch_id=launch_id, template_name=template_name,
            extension_name=extension_name, runtime=runtime,
        )
        self._launches[launch_id] = ql
        return ql

    def advance(self, launch_id: str) -> QuickLaunch | dict:
        ql = self._launches.get(launch_id)
        if not ql:
            return {"error": "Launch not found"}
        if ql.status == LaunchStatus.FAILED:
            return {"error": "Launch failed"}
        ql.steps_completed += 1
        statuses = [LaunchStatus.INITIALIZING, LaunchStatus.CONFIGURING,
                    LaunchStatus.DEPLOYING, LaunchStatus.LIVE]
        idx = min(ql.steps_completed, len(statuses) - 1)
        ql.status = statuses[idx]
        if ql.status == LaunchStatus.LIVE:
            ql.preview_url = f"https://preview.openskill.dev/{ql.extension_name}"
        return ql

    def fail(self, launch_id: str, error: str) -> bool:
        ql = self._launches.get(launch_id)
        if ql:
            ql.status = LaunchStatus.FAILED
            ql.error = error
            return True
        return False

    def get_launch(self, launch_id: str) -> QuickLaunch | None:
        return self._launches.get(launch_id)

    def list_launches(self, limit: int = 10) -> list[QuickLaunch]:
        return sorted(self._launches.values(), key=lambda l: l.started_at, reverse=True)[:limit]
