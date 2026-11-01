"""Consumer API Runbook — operational runbook with step execution tracking."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class RunbookStep:
    step_id: str
    name: str
    description: str = ""
    command: str = ""
    auto_execute: bool = False
    order: int = 0


@dataclass
class Runbook:
    runbook_id: str
    name: str
    trigger: str = ""  # incident_type, alert, manual
    steps: list[RunbookStep] = field(default_factory=list)


@dataclass
class RunbookExecution:
    execution_id: str
    runbook_id: str
    status: str = "in_progress"  # in_progress, completed, failed, aborted
    current_step: int = 0
    step_results: dict[str, dict] = field(default_factory=dict)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class RunbookManager:
    """Manage operational runbooks with step execution tracking."""

    _runbooks: dict[str, Runbook] = field(default_factory=dict)
    _executions: dict[str, RunbookExecution] = field(default_factory=dict)

    def create_runbook(self, runbook: Runbook) -> dict:
        if runbook.runbook_id in self._runbooks:
            raise ValueError(f"Runbook {runbook.runbook_id} already exists")
        if not runbook.steps:
            raise ValueError("Runbook must have at least one step")
        runbook.steps.sort(key=lambda s: s.order)
        self._runbooks[runbook.runbook_id] = runbook
        logger.info("runbook_created", runbook_id=runbook.runbook_id)
        return {"runbook_id": runbook.runbook_id, "steps": len(runbook.steps)}

    def start_execution(self, execution_id: str, runbook_id: str) -> dict:
        runbook = self._runbooks.get(runbook_id)
        if not runbook:
            raise ValueError(f"Runbook {runbook_id} not found")
        execution = RunbookExecution(execution_id=execution_id, runbook_id=runbook_id)
        self._executions[execution_id] = execution
        logger.info("runbook_started", execution_id=execution_id)
        first = runbook.steps[0] if runbook.steps else None
        return {"execution_id": execution_id, "status": "in_progress",
                "next_step": first.name if first else None}

    def complete_step(self, execution_id: str, step_id: str,
                      success: bool = True, output: str = "") -> dict:
        execution = self._executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        runbook = self._runbooks.get(execution.runbook_id)
        if not runbook:
            raise ValueError("Runbook not found")
        execution.step_results[step_id] = {
            "success": success, "output": output,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        execution.current_step += 1
        if not success:
            execution.status = "failed"
            return {"execution_id": execution_id, "status": "failed", "failed_step": step_id}
        if execution.current_step >= len(runbook.steps):
            execution.status = "completed"
            return {"execution_id": execution_id, "status": "completed"}
        next_step = runbook.steps[execution.current_step]
        return {"execution_id": execution_id, "status": "in_progress",
                "next_step": next_step.name, "progress": f"{execution.current_step}/{len(runbook.steps)}"}

    def abort(self, execution_id: str) -> dict:
        execution = self._executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")
        execution.status = "aborted"
        return {"execution_id": execution_id, "status": "aborted"}

    def get_execution(self, execution_id: str) -> dict | None:
        ex = self._executions.get(execution_id)
        if not ex:
            return None
        runbook = self._runbooks.get(ex.runbook_id)
        total = len(runbook.steps) if runbook else 0
        return {
            "execution_id": ex.execution_id, "runbook_id": ex.runbook_id,
            "status": ex.status, "progress": f"{ex.current_step}/{total}",
            "steps_completed": len(ex.step_results),
        }

    def list_runbooks(self) -> list[dict]:
        return [{"runbook_id": r.runbook_id, "name": r.name,
                 "trigger": r.trigger, "steps": len(r.steps)}
                for r in self._runbooks.values()]

    def get_stats(self) -> dict:
        execs = list(self._executions.values())
        return {
            "total_runbooks": len(self._runbooks),
            "total_executions": len(execs),
            "completed": sum(1 for e in execs if e.status == "completed"),
            "failed": sum(1 for e in execs if e.status == "failed"),
        }
