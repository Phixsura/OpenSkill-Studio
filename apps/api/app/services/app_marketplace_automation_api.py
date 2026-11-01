"""Automation API — define, trigger, and manage automated workflows.

Enables developers to create event-driven automations that respond
to platform events (submissions, reviews, deployments, etc).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class TriggerType(str, Enum):
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"
    EVENT = "event"
    MANUAL = "manual"


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


@dataclass
class WorkflowStep:
    step_id: str
    action: str
    params: dict = field(default_factory=dict)
    condition: str | None = None
    timeout_seconds: int = 300


@dataclass
class Workflow:
    workflow_id: str
    name: str
    trigger_type: TriggerType
    trigger_config: dict
    steps: list[WorkflowStep]
    owner: str
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: str = ""
    run_count: int = 0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class AutomationEngine:
    """Manages workflow definitions and execution."""

    def __init__(self):
        self._workflows: dict[str, Workflow] = {}
        self._run_log: list[dict] = []

    def create_workflow(
        self, workflow_id: str, name: str, trigger_type: TriggerType,
        trigger_config: dict, steps: list[dict], owner: str,
    ) -> Workflow:
        """Create a new automation workflow."""
        parsed_steps = [
            WorkflowStep(
                step_id=s.get("step_id", f"step-{i}"),
                action=s["action"],
                params=s.get("params", {}),
                condition=s.get("condition"),
                timeout_seconds=s.get("timeout_seconds", 300),
            )
            for i, s in enumerate(steps)
        ]
        wf = Workflow(
            workflow_id=workflow_id, name=name,
            trigger_type=trigger_type, trigger_config=trigger_config,
            steps=parsed_steps, owner=owner,
        )
        self._workflows[workflow_id] = wf
        return wf

    def activate(self, workflow_id: str) -> bool:
        wf = self._workflows.get(workflow_id)
        if wf and wf.status in (WorkflowStatus.DRAFT, WorkflowStatus.PAUSED):
            wf.status = WorkflowStatus.ACTIVE
            return True
        return False

    def pause(self, workflow_id: str) -> bool:
        wf = self._workflows.get(workflow_id)
        if wf and wf.status == WorkflowStatus.ACTIVE:
            wf.status = WorkflowStatus.PAUSED
            return True
        return False

    def trigger(self, workflow_id: str, event_data: dict | None = None) -> dict | None:
        """Trigger a workflow execution."""
        wf = self._workflows.get(workflow_id)
        if not wf or wf.status != WorkflowStatus.ACTIVE:
            return None
        wf.run_count += 1
        run = {
            "workflow_id": workflow_id,
            "run_number": wf.run_count,
            "triggered_at": datetime.now(timezone.utc).isoformat(),
            "event_data": event_data or {},
            "steps_executed": len(wf.steps),
            "result": "success",
        }
        self._run_log.append(run)
        return run

    def get_workflow(self, workflow_id: str) -> Workflow | None:
        return self._workflows.get(workflow_id)

    def list_workflows(self, owner: str | None = None) -> list[Workflow]:
        wfs = list(self._workflows.values())
        if owner:
            wfs = [w for w in wfs if w.owner == owner]
        return wfs

    def get_run_log(self, workflow_id: str | None = None) -> list[dict]:
        if workflow_id:
            return [r for r in self._run_log if r["workflow_id"] == workflow_id]
        return list(self._run_log)
