"""Automation Trigger Registry — register and manage automation triggers."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class AutomationTrigger:
    trigger_id: str
    name: str
    event_type: str  # schedule, webhook, event, manual
    config: dict = field(default_factory=dict)
    enabled: bool = True
    last_fired: float = 0.0
    fire_count: int = 0
    created_by: str = ""


class AutomationTriggerRegistryService:
    def __init__(self):
        self._triggers: dict[str, AutomationTrigger] = {}
        self._counter = 0

    def register(self, name: str, event_type: str, config: dict,
                 created_by: str) -> AutomationTrigger:
        self._counter += 1
        tid = f"trg-{self._counter}"
        t = AutomationTrigger(trigger_id=tid, name=name, event_type=event_type,
                              config=config, created_by=created_by)
        self._triggers[tid] = t
        return t

    def fire(self, trigger_id: str) -> dict | None:
        t = self._triggers.get(trigger_id)
        if not t or not t.enabled:
            return None
        t.last_fired = time.time()
        t.fire_count += 1
        return {"trigger_id": t.trigger_id, "event": t.event_type,
                "config": t.config, "fire_count": t.fire_count}

    def toggle(self, trigger_id: str, enabled: bool) -> bool:
        t = self._triggers.get(trigger_id)
        if not t: return False
        t.enabled = enabled
        return True

    def list_by_type(self, event_type: str) -> list[AutomationTrigger]:
        return [t for t in self._triggers.values() if t.event_type == event_type]

    def list_all(self) -> list[AutomationTrigger]:
        return list(self._triggers.values())

    def delete(self, trigger_id: str) -> bool:
        return self._triggers.pop(trigger_id, None) is not None
