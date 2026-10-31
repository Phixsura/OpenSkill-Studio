"""Workflow Trigger — define and fire event-driven triggers for extension workflows.

Supports cron schedules, webhook events, manual triggers, and conditional
expressions that evaluate against event payloads to decide execution.
"""
from __future__ import annotations
import re
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class TriggerType(str, Enum):
    WEBHOOK = "webhook"
    CRON = "cron"
    MANUAL = "manual"
    EVENT = "event"


class TriggerStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DISABLED = "disabled"


@dataclass
class TriggerCondition:
    field: str
    operator: str  # eq, ne, gt, lt, contains, matches
    value: str


@dataclass
class WorkflowTrigger:
    trigger_id: str
    extension_id: str
    workflow_id: str
    trigger_type: TriggerType
    name: str
    status: TriggerStatus = TriggerStatus.ACTIVE
    conditions: list[TriggerCondition] = field(default_factory=list)
    cron_expression: str = ""
    event_type: str = ""
    fire_count: int = 0
    last_fired: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


VALID_OPERATORS = {"eq", "ne", "gt", "lt", "contains", "matches"}


class WorkflowTriggerService:
    """Manages workflow triggers with conditional evaluation."""

    def __init__(self):
        self._triggers: dict[str, WorkflowTrigger] = {}

    def create_trigger(self, extension_id: str, workflow_id: str,
                       trigger_type: TriggerType, name: str,
                       conditions: list[dict] | None = None,
                       cron_expression: str = "",
                       event_type: str = "") -> WorkflowTrigger:
        trigger_id = f"trg_{secrets.token_urlsafe(12)}"
        parsed_conditions = []
        for c in (conditions or []):
            op = c.get("operator", "eq")
            if op not in VALID_OPERATORS:
                raise ValueError(f"Invalid operator: {op}")
            parsed_conditions.append(TriggerCondition(
                field=c["field"], operator=op, value=str(c["value"])
            ))
        if trigger_type == TriggerType.CRON and not cron_expression:
            raise ValueError("Cron triggers require a cron_expression")
        if trigger_type == TriggerType.EVENT and not event_type:
            raise ValueError("Event triggers require an event_type")

        t = WorkflowTrigger(
            trigger_id=trigger_id, extension_id=extension_id,
            workflow_id=workflow_id, trigger_type=trigger_type,
            name=name, conditions=parsed_conditions,
            cron_expression=cron_expression, event_type=event_type,
        )
        self._triggers[trigger_id] = t
        return t

    def _check_condition(self, cond: TriggerCondition, sval: str) -> bool:
        if cond.operator == "eq":
            return sval == cond.value
        elif cond.operator == "ne":
            return sval != cond.value
        elif cond.operator == "gt":
            try:
                return float(sval) > float(cond.value)
            except ValueError:
                return False
        elif cond.operator == "lt":
            try:
                return float(sval) < float(cond.value)
            except ValueError:
                return False
        elif cond.operator == "contains":
            return cond.value in sval
        elif cond.operator == "matches":
            try:
                return bool(re.fullmatch(cond.value, sval))
            except re.error:
                return False
        return False  # unknown operator — fail closed

    def evaluate_conditions(self, trigger_id: str, payload: dict) -> bool:
        t = self._triggers.get(trigger_id)
        if not t or t.status != TriggerStatus.ACTIVE:
            return False
        for cond in t.conditions:
            val = payload.get(cond.field)
            if val is None:
                return False
            if not self._check_condition(cond, str(val)):
                return False
        return True

    def fire(self, trigger_id: str, payload: dict | None = None) -> dict:
        t = self._triggers.get(trigger_id)
        if not t:
            return {"fired": False, "reason": "Trigger not found"}
        if t.status != TriggerStatus.ACTIVE:
            return {"fired": False, "reason": f"Trigger is {t.status.value}"}
        if t.conditions:
            if not self.evaluate_conditions(trigger_id, payload or {}):
                return {"fired": False, "reason": "Conditions not met"}
        t.fire_count += 1
        t.last_fired = datetime.now(timezone.utc).isoformat()
        return {
            "fired": True, "trigger_id": trigger_id,
            "workflow_id": t.workflow_id, "fire_count": t.fire_count,
        }

    def pause(self, trigger_id: str) -> bool:
        t = self._triggers.get(trigger_id)
        if t and t.status == TriggerStatus.ACTIVE:
            t.status = TriggerStatus.PAUSED
            return True
        return False

    def resume(self, trigger_id: str) -> bool:
        t = self._triggers.get(trigger_id)
        if t and t.status == TriggerStatus.PAUSED:
            t.status = TriggerStatus.ACTIVE
            return True
        return False

    def list_triggers(self, extension_id: str, workflow_id: str | None = None) -> list[WorkflowTrigger]:
        triggers = [t for t in self._triggers.values() if t.extension_id == extension_id]
        if workflow_id:
            triggers = [t for t in triggers if t.workflow_id == workflow_id]
        return triggers
