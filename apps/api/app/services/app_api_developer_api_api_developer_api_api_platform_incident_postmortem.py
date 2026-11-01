"""App API Developer Platform Incident Postmortem — structured incident review."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class Postmortem:
    postmortem_id: str
    incident_id: str
    title: str
    severity: str  # "sev1", "sev2", "sev3"
    root_cause: str
    impact_summary: str
    action_items: list[str] = field(default_factory=list)
    timeline: list[str] = field(default_factory=list)
    status: str = "draft"  # "draft", "review", "published"
    duration_minutes: int = 0
    published_at: float | None = None

class AppAPIDeveloperAPIApiDeveloperApiApiPlatformIncidentPostmortem:
    def __init__(self) -> None:
        self._postmortems: dict[tuple[str, str], Postmortem] = {}

    def create(self, installation_id: str, postmortem_id: str, incident_id: str, title: str, severity: str, root_cause: str, impact_summary: str, action_items: list[str] | None = None, duration_minutes: int = 0) -> Postmortem:
        if not installation_id: raise ValueError("installation_id is required")
        if severity not in ("sev1", "sev2", "sev3"): raise ValueError("invalid severity")
        key = (installation_id, postmortem_id)
        if key in self._postmortems: raise ValueError(f"Postmortem {postmortem_id} exists")
        p = Postmortem(postmortem_id=postmortem_id, incident_id=incident_id, title=title, severity=severity, root_cause=root_cause, impact_summary=impact_summary, action_items=action_items or [], duration_minutes=duration_minutes)
        self._postmortems[key] = p
        return p

    def publish(self, installation_id: str, postmortem_id: str) -> Postmortem:
        p = self._get(installation_id, postmortem_id)
        if not p.action_items: raise ValueError("Must have action items before publishing")
        p.status = "published"
        p.published_at = time.time()
        return p

    def open_action_items(self, installation_id: str) -> int:
        return sum(len(p.action_items) for (inst, _), p in self._postmortems.items() if inst == installation_id and p.status == "published")

    def by_severity(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), p in self._postmortems.items():
            if inst == installation_id: counts[p.severity] = counts.get(p.severity, 0) + 1
        return counts

    def all_postmortems(self, installation_id: str) -> list[Postmortem]:
        return [p for (inst, _), p in self._postmortems.items() if inst == installation_id]

    def _get(self, installation_id: str, postmortem_id: str) -> Postmortem:
        key = (installation_id, postmortem_id)
        p = self._postmortems.get(key)
        if p is None: raise KeyError(f"Postmortem {postmortem_id} not found")
        return p
