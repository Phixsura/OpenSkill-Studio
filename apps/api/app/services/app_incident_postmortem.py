"""App Incident Postmortem — create and track postmortems for incidents.

Manages postmortem documentation:
- Create postmortems with timeline, root cause, action items
- Track action item completion
- Link to incidents
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ActionItem:
    """An action item from a postmortem."""

    action_id: str
    description: str
    owner: str
    completed: bool = False


@dataclass
class Postmortem:
    """An incident postmortem."""

    postmortem_id: str
    incident_id: str
    title: str
    summary: str
    root_cause: str
    impact: str
    action_items: list[ActionItem] = field(default_factory=list)

    @property
    def actions_completed(self) -> int:
        return sum(1 for a in self.action_items if a.completed)

    @property
    def completion_pct(self) -> float:
        if not self.action_items:
            return 100.0
        return round(self.actions_completed / len(self.action_items) * 100, 1)


class AppIncidentPostmortem:
    """Create and track incident postmortems."""

    def __init__(self) -> None:
        self._postmortems: dict[tuple[str, str], Postmortem] = {}

    def create_postmortem(
        self,
        installation_id: str,
        postmortem_id: str,
        incident_id: str,
        title: str,
        summary: str,
        root_cause: str,
        impact: str,
        action_items: list[dict] | None = None,
    ) -> Postmortem:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not postmortem_id:
            raise ValueError("postmortem_id is required")
        if not root_cause:
            raise ValueError("root_cause is required")

        items = [
            ActionItem(action_id=a["action_id"], description=a["description"], owner=a["owner"])
            for a in (action_items or [])
        ]

        pm = Postmortem(
            postmortem_id=postmortem_id, incident_id=incident_id,
            title=title, summary=summary, root_cause=root_cause,
            impact=impact, action_items=items,
        )
        self._postmortems[(installation_id, postmortem_id)] = pm
        return pm

    def complete_action(
        self, installation_id: str, postmortem_id: str, action_id: str
    ) -> ActionItem:
        pm = self._get(installation_id, postmortem_id)
        for a in pm.action_items:
            if a.action_id == action_id:
                a.completed = True
                return a
        raise KeyError(f"Action {action_id} not found")

    def get_postmortem(self, installation_id: str, postmortem_id: str) -> Postmortem:
        return self._get(installation_id, postmortem_id)

    def list_postmortems(self, installation_id: str) -> list[Postmortem]:
        return [pm for (inst, _), pm in self._postmortems.items() if inst == installation_id]

    def _get(self, installation_id: str, postmortem_id: str) -> Postmortem:
        key = (installation_id, postmortem_id)
        pm = self._postmortems.get(key)
        if pm is None:
            raise KeyError(f"Postmortem {postmortem_id} not found")
        return pm
