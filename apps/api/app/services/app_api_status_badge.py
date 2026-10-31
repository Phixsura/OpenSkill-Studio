"""App API Status Badge — generate dynamic status badges.

Manages status badges:
- Define badge configs (label, status, color)
- Generate badge data for rendering
- Track badge views
- Per-installation scoped badges
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class StatusBadge:
    """A status badge configuration."""

    badge_id: str
    label: str
    status: str
    color: str = "green"  # green, yellow, red, blue, gray
    views: int = 0


VALID_COLORS = {"green", "yellow", "red", "blue", "gray"}


class AppAPIStatusBadge:
    """Generate dynamic status badges."""

    def __init__(self) -> None:
        self._badges: dict[tuple[str, str], StatusBadge] = {}

    def create(
        self, installation_id: str, badge_id: str, label: str,
        status: str, color: str = "green",
    ) -> StatusBadge:
        if not installation_id:
            raise ValueError("installation_id is required")
        if color not in VALID_COLORS:
            raise ValueError(f"color must be one of {VALID_COLORS}")

        badge = StatusBadge(badge_id=badge_id, label=label, status=status, color=color)
        self._badges[(installation_id, badge_id)] = badge
        return badge

    def update_status(self, installation_id: str, badge_id: str, status: str, color: str | None = None) -> StatusBadge:
        b = self._get(installation_id, badge_id)
        b.status = status
        if color:
            if color not in VALID_COLORS:
                raise ValueError(f"color must be one of {VALID_COLORS}")
            b.color = color
        return b

    def record_view(self, installation_id: str, badge_id: str) -> StatusBadge:
        b = self._get(installation_id, badge_id)
        b.views += 1
        return b

    def list_badges(self, installation_id: str) -> list[StatusBadge]:
        return [b for (inst, _), b in self._badges.items() if inst == installation_id]

    def _get(self, installation_id: str, badge_id: str) -> StatusBadge:
        key = (installation_id, badge_id)
        b = self._badges.get(key)
        if b is None:
            raise KeyError(f"Badge {badge_id} not found")
        return b
