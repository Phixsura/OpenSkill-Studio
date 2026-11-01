"""App API Developer Consumer Onboarding Funnel — track developer activation steps."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

FUNNEL_STEPS = ["signup", "api_key_created", "first_request", "webhook_configured", "production_traffic"]

@dataclass
class FunnelMetrics:
    step: str
    entered: int = 0
    completed: int = 0

    @property
    def conversion_rate(self) -> float:
        return round(self.completed / self.entered * 100, 1) if self.entered > 0 else 0.0

class AppAPIDeveloperAPIApiConsumerOnboardingFunnel:
    def __init__(self) -> None:
        self._metrics: dict[tuple[str, str], FunnelMetrics] = {}
        self._consumer_steps: dict[tuple[str, str], set[str]] = {}

    def enter_step(self, installation_id: str, consumer_id: str, step: str) -> FunnelMetrics:
        if not installation_id: raise ValueError("installation_id is required")
        if step not in FUNNEL_STEPS: raise ValueError(f"Invalid step: {step}")
        key = (installation_id, step)
        if key not in self._metrics:
            self._metrics[key] = FunnelMetrics(step=step)
        ck = (installation_id, consumer_id)
        steps = self._consumer_steps.setdefault(ck, set())
        if step not in steps:
            self._metrics[key].entered += 1
            steps.add(step)
        return self._metrics[key]

    def complete_step(self, installation_id: str, consumer_id: str, step: str) -> FunnelMetrics:
        m = self.enter_step(installation_id, consumer_id, step)
        m.completed += 1
        return m

    def funnel(self, installation_id: str) -> list[FunnelMetrics]:
        return [self._metrics.get((installation_id, s), FunnelMetrics(step=s)) for s in FUNNEL_STEPS]

    def drop_off_step(self, installation_id: str) -> str | None:
        metrics = self.funnel(installation_id)
        worst_rate = 100.0
        worst_step = None
        for m in metrics:
            if m.entered > 0 and m.conversion_rate < worst_rate:
                worst_rate = m.conversion_rate
                worst_step = m.step
        return worst_step

    def overall_conversion(self, installation_id: str) -> float:
        first = self._metrics.get((installation_id, FUNNEL_STEPS[0]))
        last = self._metrics.get((installation_id, FUNNEL_STEPS[-1]))
        if not first or first.entered == 0: return 0.0
        return round((last.completed if last else 0) / first.entered * 100, 1)
