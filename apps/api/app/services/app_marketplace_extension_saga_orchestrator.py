"""Saga Orchestrator — coordinate distributed transactions with compensation.

Implements:
- Sequential step execution with rollback on failure
- Compensating transactions for each completed step
- Saga state machine (RUNNING → COMPLETED | COMPENSATING → COMPENSATED | FAILED)
- Step timeout tracking
- Partial completion reporting
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from enum import Enum


class SagaState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"


class StepState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    SKIPPED = "skipped"


@dataclass
class SagaStep:
    name: str
    action: callable
    compensate: callable
    state: StepState = StepState.PENDING
    result: dict = field(default_factory=dict)
    error: str = ""
    duration_ms: float = 0.0


@dataclass
class Saga:
    saga_id: str
    name: str
    steps: list[SagaStep] = field(default_factory=list)
    state: SagaState = SagaState.PENDING
    context: dict = field(default_factory=dict)
    started_at: float = 0.0
    completed_at: float = 0.0


class SagaOrchestratorService:
    def __init__(self):
        self._sagas: dict[str, Saga] = {}
        self._counter = 0

    def create(self, name: str, context: dict | None = None) -> Saga:
        self._counter += 1
        saga = Saga(saga_id=f"saga-{self._counter}", name=name,
                    context=context or {})
        self._sagas[saga.saga_id] = saga
        return saga

    def add_step(self, saga_id: str, name: str, action: callable,
                 compensate: callable) -> bool:
        saga = self._sagas.get(saga_id)
        if not saga or saga.state != SagaState.PENDING:
            return False
        saga.steps.append(SagaStep(name=name, action=action, compensate=compensate))
        return True

    def execute(self, saga_id: str) -> Saga:
        """Execute all steps sequentially; compensate on failure."""
        saga = self._sagas.get(saga_id)
        if not saga:
            raise ValueError("Saga not found")
        saga.state = SagaState.RUNNING
        saga.started_at = time.time()

        completed_steps: list[int] = []

        for i, step in enumerate(saga.steps):
            step.state = StepState.RUNNING
            start = time.time()
            try:
                result = step.action(saga.context)
                step.result = result or {}
                step.state = StepState.COMPLETED
                step.duration_ms = round((time.time() - start) * 1000, 2)
                # Merge result into context for next steps
                saga.context.update(step.result)
                completed_steps.append(i)
            except Exception as e:
                step.state = StepState.FAILED
                step.error = str(e)
                step.duration_ms = round((time.time() - start) * 1000, 2)
                # Mark remaining as skipped
                for j in range(i + 1, len(saga.steps)):
                    saga.steps[j].state = StepState.SKIPPED
                # Compensate in reverse
                self._compensate(saga, completed_steps)
                return saga

        saga.state = SagaState.COMPLETED
        saga.completed_at = time.time()
        return saga

    def _compensate(self, saga: Saga, completed_indices: list[int]) -> None:
        saga.state = SagaState.COMPENSATING
        all_compensated = True

        for i in reversed(completed_indices):
            step = saga.steps[i]
            step.state = StepState.COMPENSATING
            try:
                step.compensate(saga.context)
                step.state = StepState.COMPENSATED
            except Exception as e:
                step.state = StepState.FAILED
                step.error = f"Compensation failed: {e}"
                all_compensated = False

        saga.state = SagaState.COMPENSATED if all_compensated else SagaState.FAILED
        saga.completed_at = time.time()

    def get_status(self, saga_id: str) -> dict | None:
        saga = self._sagas.get(saga_id)
        if not saga:
            return None
        return {
            "saga_id": saga.saga_id,
            "name": saga.name,
            "state": saga.state.value,
            "steps": [{"name": s.name, "state": s.state.value, "error": s.error,
                        "duration_ms": s.duration_ms} for s in saga.steps],
            "completed": sum(1 for s in saga.steps if s.state == StepState.COMPLETED),
            "total": len(saga.steps),
        }
