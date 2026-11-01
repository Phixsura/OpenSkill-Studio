"""API Consumer Lifecycle — manage consumer states from registration to offboarding."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class LifecycleState(str, Enum):
    REGISTERED = "registered"
    ONBOARDING = "onboarding"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    OFFBOARDING = "offboarding"
    DEACTIVATED = "deactivated"

VALID_TRANSITIONS = {
    LifecycleState.REGISTERED: {LifecycleState.ONBOARDING},
    LifecycleState.ONBOARDING: {LifecycleState.ACTIVE},
    LifecycleState.ACTIVE: {LifecycleState.SUSPENDED, LifecycleState.OFFBOARDING},
    LifecycleState.SUSPENDED: {LifecycleState.ACTIVE, LifecycleState.OFFBOARDING},
    LifecycleState.OFFBOARDING: {LifecycleState.DEACTIVATED},
    LifecycleState.DEACTIVATED: set(),
}

@dataclass
class ConsumerLifecycle:
    consumer_id: str
    state: LifecycleState = LifecycleState.REGISTERED
    registered_at: float = field(default_factory=time.time)
    last_transition_at: float = field(default_factory=time.time)
    transition_count: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerLifecycle:
    def __init__(self) -> None:
        self._consumers: dict[tuple[str, str], ConsumerLifecycle] = {}

    def register(self, installation_id: str, consumer_id: str) -> ConsumerLifecycle:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key in self._consumers: raise ValueError(f"Consumer {consumer_id} already registered")
        cl = ConsumerLifecycle(consumer_id=consumer_id)
        self._consumers[key] = cl
        return cl

    def transition(self, installation_id: str, consumer_id: str, target: LifecycleState) -> ConsumerLifecycle:
        cl = self._get(installation_id, consumer_id)
        allowed = VALID_TRANSITIONS.get(cl.state, set())
        if target not in allowed:
            raise ValueError(f"Cannot transition from {cl.state.value} to {target.value}")
        cl.state = target
        cl.last_transition_at = time.time()
        cl.transition_count += 1
        return cl

    def consumers_by_state(self, installation_id: str) -> dict[str, int]:
        result: dict[str, int] = {}
        for (inst, _), cl in self._consumers.items():
            if inst == installation_id:
                result[cl.state.value] = result.get(cl.state.value, 0) + 1
        return result

    def list_consumers(self, installation_id: str, state: LifecycleState | None = None) -> list[ConsumerLifecycle]:
        consumers = [cl for (inst, _), cl in self._consumers.items() if inst == installation_id]
        if state: consumers = [cl for cl in consumers if cl.state == state]
        return consumers

    def _get(self, installation_id: str, consumer_id: str) -> ConsumerLifecycle:
        cl = self._consumers.get((installation_id, consumer_id))
        if cl is None: raise KeyError(f"Consumer {consumer_id} not found")
        return cl
