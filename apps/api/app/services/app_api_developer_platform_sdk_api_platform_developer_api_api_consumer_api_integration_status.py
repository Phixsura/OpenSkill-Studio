"""API Consumer Integration Status — track consumer integration readiness."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import structlog

log = structlog.get_logger()

class IntegrationPhase(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    PRODUCTION = "production"

@dataclass
class IntegrationCheck:
    check_id: str
    name: str
    passed: bool = False
    required: bool = True

@dataclass
class IntegrationStatus:
    consumer_id: str
    phase: IntegrationPhase = IntegrationPhase.NOT_STARTED
    checks: list[IntegrationCheck] = field(default_factory=list)

    @property
    def ready_for_production(self) -> bool:
        required = [c for c in self.checks if c.required]
        return bool(required) and all(c.passed for c in required)

    @property
    def completion_pct(self) -> float:
        if not self.checks: return 0.0
        return round(sum(1 for c in self.checks if c.passed) / len(self.checks) * 100, 1)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiIntegrationStatus:
    def __init__(self) -> None:
        self._statuses: dict[tuple[str, str], IntegrationStatus] = {}

    def create_status(self, installation_id: str, consumer_id: str, checks: list[IntegrationCheck]) -> IntegrationStatus:
        if not installation_id: raise ValueError("installation_id is required")
        if not checks: raise ValueError("At least one check required")
        key = (installation_id, consumer_id)
        status = IntegrationStatus(consumer_id=consumer_id, checks=checks)
        self._statuses[key] = status
        return status

    def pass_check(self, installation_id: str, consumer_id: str, check_id: str) -> IntegrationStatus:
        status = self._get(installation_id, consumer_id)
        for c in status.checks:
            if c.check_id == check_id: c.passed = True; break
        if status.ready_for_production: status.phase = IntegrationPhase.PRODUCTION
        elif status.completion_pct > 0: status.phase = IntegrationPhase.IN_PROGRESS
        return status

    def get_status(self, installation_id: str, consumer_id: str) -> IntegrationStatus:
        return self._get(installation_id, consumer_id)

    def not_ready(self, installation_id: str) -> list[IntegrationStatus]:
        return [s for (inst, _), s in self._statuses.items() if inst == installation_id and not s.ready_for_production]

    def list_statuses(self, installation_id: str) -> list[IntegrationStatus]:
        return [s for (inst, _), s in self._statuses.items() if inst == installation_id]

    def _get(self, installation_id: str, consumer_id: str) -> IntegrationStatus:
        s = self._statuses.get((installation_id, consumer_id))
        if s is None: raise KeyError(f"Status for {consumer_id} not found")
        return s
