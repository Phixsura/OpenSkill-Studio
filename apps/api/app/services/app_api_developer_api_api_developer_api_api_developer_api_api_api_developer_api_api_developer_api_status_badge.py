"""App API Developer Status Badge — generate embeddable status badges."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class StatusBadge:
    badge_id: str
    label: str
    value: str
    color: str  # "green", "yellow", "red", "blue", "gray"
    style: str = "flat"  # "flat", "flat-square", "plastic"

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiDeveloperApiStatusBadge:
    def __init__(self) -> None:
        self._badges: dict[tuple[str, str], StatusBadge] = {}

    def create(self, installation_id: str, badge_id: str, label: str, value: str, color: str, style: str = "flat") -> StatusBadge:
        if not installation_id: raise ValueError("installation_id is required")
        if color not in ("green", "yellow", "red", "blue", "gray"): raise ValueError("invalid color")
        if style not in ("flat", "flat-square", "plastic"): raise ValueError("invalid style")
        key = (installation_id, badge_id)
        b = StatusBadge(badge_id=badge_id, label=label, value=value, color=color, style=style)
        self._badges[key] = b
        return b

    def generate_uptime_badge(self, installation_id: str, uptime_pct: float) -> StatusBadge:
        color = "green" if uptime_pct >= 99.9 else "yellow" if uptime_pct >= 99 else "red"
        return self.create(installation_id, "uptime", "uptime", f"{uptime_pct}%", color)

    def generate_build_badge(self, installation_id: str, passing: bool) -> StatusBadge:
        return self.create(installation_id, "build", "build", "passing" if passing else "failing", "green" if passing else "red")

    def get(self, installation_id: str, badge_id: str) -> StatusBadge | None:
        return self._badges.get((installation_id, badge_id))

    def all_badges(self, installation_id: str) -> list[StatusBadge]:
        return [b for (inst, _), b in self._badges.items() if inst == installation_id]

    def render_svg(self, installation_id: str, badge_id: str) -> str:
        b = self._badges.get((installation_id, badge_id))
        if b is None: raise KeyError(f"Badge {badge_id} not found")
        colors = {"green": "#4c1", "yellow": "#dfb317", "red": "#e05d44", "blue": "#007ec6", "gray": "#555"}
        c = colors.get(b.color, "#555")
        return f'<svg xmlns="http://www.w3.org/2000/svg"><rect fill="#555" width="80" height="20"/><rect x="80" fill="{c}" width="60" height="20"/><text x="40" y="14" fill="#fff">{b.label}</text><text x="110" y="14" fill="#fff">{b.value}</text></svg>'
