"""API Consumer Endpoint Warmup — pre-warm endpoint caches and connections."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class WarmupTarget:
    endpoint: str
    method: str
    warmup_requests: int = 5
    completed: bool = False
    latency_ms: float = 0.0
    warmed_at: float = 0.0

@dataclass
class WarmupPlan:
    plan_id: str
    targets: list[WarmupTarget] = field(default_factory=list)
    started_at: float = 0.0
    completed_at: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointWarmup:
    def __init__(self) -> None:
        self._plans: dict[tuple[str, str], WarmupPlan] = {}

    def create_plan(self, installation_id: str, plan_id: str, targets: list[WarmupTarget]) -> WarmupPlan:
        if not installation_id: raise ValueError("installation_id is required")
        if not targets: raise ValueError("At least one target required")
        plan = WarmupPlan(plan_id=plan_id, targets=targets, started_at=time.time())
        self._plans[(installation_id, plan_id)] = plan
        return plan

    def complete_target(self, installation_id: str, plan_id: str, endpoint: str, method: str, latency_ms: float) -> WarmupPlan:
        plan = self._get(installation_id, plan_id)
        for t in plan.targets:
            if t.endpoint == endpoint and t.method == method.upper():
                t.completed = True
                t.latency_ms = latency_ms
                t.warmed_at = time.time()
                break
        if all(t.completed for t in plan.targets):
            plan.completed_at = time.time()
        return plan

    def progress(self, installation_id: str, plan_id: str) -> float:
        plan = self._get(installation_id, plan_id)
        if not plan.targets: return 0.0
        done = sum(1 for t in plan.targets if t.completed)
        return round((done / len(plan.targets)) * 100, 1)

    def is_complete(self, installation_id: str, plan_id: str) -> bool:
        plan = self._get(installation_id, plan_id)
        return plan.completed_at > 0

    def list_plans(self, installation_id: str) -> list[WarmupPlan]:
        return [p for (inst, _), p in self._plans.items() if inst == installation_id]

    def _get(self, installation_id: str, plan_id: str) -> WarmupPlan:
        p = self._plans.get((installation_id, plan_id))
        if p is None: raise KeyError(f"Plan {plan_id} not found")
        return p
