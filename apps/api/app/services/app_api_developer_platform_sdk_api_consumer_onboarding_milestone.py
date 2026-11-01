"""App API Developer Consumer Onboarding Milestone — track consumer onboarding milestones."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

MILESTONES = ["registered", "api_key_created", "first_api_call", "first_webhook", "production_traffic", "first_payment"]

@dataclass
class ConsumerMilestones:
    consumer_id: str
    achieved: dict[str, float] = field(default_factory=dict)  # milestone -> timestamp

    @property
    def completed_count(self) -> int:
        return len(self.achieved)

    @property
    def completion_pct(self) -> float:
        return round(self.completed_count / len(MILESTONES) * 100, 1)

    @property
    def next_milestone(self) -> str | None:
        for m in MILESTONES:
            if m not in self.achieved: return m
        return None

    @property
    def fully_onboarded(self) -> bool:
        return self.completed_count == len(MILESTONES)

class AppAPIDeveloperPlatformSDKApiConsumerOnboardingMilestone:
    def __init__(self) -> None:
        self._milestones: dict[tuple[str, str], ConsumerMilestones] = {}

    def achieve(self, installation_id: str, consumer_id: str, milestone: str) -> ConsumerMilestones:
        if not installation_id: raise ValueError("installation_id is required")
        if milestone not in MILESTONES: raise ValueError(f"Invalid milestone: {milestone}")
        key = (installation_id, consumer_id)
        if key not in self._milestones:
            self._milestones[key] = ConsumerMilestones(consumer_id=consumer_id)
        m = self._milestones[key]
        if milestone not in m.achieved:
            m.achieved[milestone] = time.time()
        return m

    def get(self, installation_id: str, consumer_id: str) -> ConsumerMilestones:
        return self._milestones.get((installation_id, consumer_id), ConsumerMilestones(consumer_id=consumer_id))

    def fully_onboarded(self, installation_id: str) -> list[ConsumerMilestones]:
        return [m for (inst, _), m in self._milestones.items() if inst == installation_id and m.fully_onboarded]

    def completion_rate(self, installation_id: str) -> float:
        consumers = [m for (inst, _), m in self._milestones.items() if inst == installation_id]
        if not consumers: return 0.0
        return round(sum(1 for c in consumers if c.fully_onboarded) / len(consumers) * 100, 1)
