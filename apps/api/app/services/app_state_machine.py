"""App State Machine — define and execute state machines for installed apps.

Manages finite state machines:
- Define states and transitions
- Guard conditions on transitions
- Transition history (audit trail)
- Per-entity state tracking
- Per-installation scoped machines
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Transition:
    """A state transition definition."""

    from_state: str
    to_state: str
    event: str
    guard: str = ""  # human-readable condition


@dataclass
class TransitionRecord:
    """Record of a state transition."""

    entity_id: str
    from_state: str
    to_state: str
    event: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class StateMachineConfig:
    """Configuration for a state machine."""

    machine_id: str
    installation_id: str
    initial_state: str
    states: list[str]
    transitions: list[Transition]


class AppStateMachine:
    """Define and execute state machines for installed apps."""

    def __init__(self) -> None:
        # (installation_id, machine_id) → StateMachineConfig
        self._machines: dict[tuple[str, str], StateMachineConfig] = {}
        # (installation_id, machine_id, entity_id) → current state
        self._entity_states: dict[tuple[str, str, str], str] = {}
        # (installation_id, machine_id, entity_id) → transition history
        self._history: dict[tuple[str, str, str], list[TransitionRecord]] = {}

    def define_machine(
        self,
        installation_id: str,
        machine_id: str,
        initial_state: str,
        states: list[str],
        transitions: list[dict],
    ) -> StateMachineConfig:
        """Define a state machine."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not machine_id:
            raise ValueError("machine_id is required")
        if len(states) < 2:
            raise ValueError("At least 2 states required")
        if initial_state not in states:
            raise ValueError(f"Initial state {initial_state} not in states")

        key = (installation_id, machine_id)
        if key in self._machines:
            raise ValueError(f"Machine {machine_id} already exists")

        trans_objs = [
            Transition(
                from_state=t["from"],
                to_state=t["to"],
                event=t["event"],
                guard=t.get("guard", ""),
            )
            for t in transitions
        ]

        # Validate all transition states exist
        for t in trans_objs:
            if t.from_state not in states:
                raise ValueError(f"Transition from_state {t.from_state} not in states")
            if t.to_state not in states:
                raise ValueError(f"Transition to_state {t.to_state} not in states")

        config = StateMachineConfig(
            machine_id=machine_id,
            installation_id=installation_id,
            initial_state=initial_state,
            states=states,
            transitions=trans_objs,
        )
        self._machines[key] = config
        return config

    def get_state(
        self, installation_id: str, machine_id: str, entity_id: str
    ) -> str:
        """Get current state of an entity. Returns initial_state if new."""
        machine = self._get_machine(installation_id, machine_id)
        key = (installation_id, machine_id, entity_id)
        return self._entity_states.get(key, machine.initial_state)

    def send_event(
        self,
        installation_id: str,
        machine_id: str,
        entity_id: str,
        event: str,
        now: float | None = None,
    ) -> str:
        """Send an event to trigger a transition. Returns new state."""
        machine = self._get_machine(installation_id, machine_id)
        current = self.get_state(installation_id, machine_id, entity_id)

        # Find matching transition
        matching = [
            t for t in machine.transitions
            if t.from_state == current and t.event == event
        ]

        if not matching:
            raise ValueError(
                f"No transition from {current} on event {event}"
            )

        transition = matching[0]
        now = now or time.time()

        # Record transition
        entity_key = (installation_id, machine_id, entity_id)
        self._entity_states[entity_key] = transition.to_state
        record = TransitionRecord(
            entity_id=entity_id,
            from_state=current,
            to_state=transition.to_state,
            event=event,
            timestamp=now,
        )
        self._history.setdefault(entity_key, []).append(record)

        return transition.to_state

    def get_available_events(
        self, installation_id: str, machine_id: str, entity_id: str
    ) -> list[str]:
        """Get events available from the current state."""
        machine = self._get_machine(installation_id, machine_id)
        current = self.get_state(installation_id, machine_id, entity_id)
        return [t.event for t in machine.transitions if t.from_state == current]

    def get_history(
        self,
        installation_id: str,
        machine_id: str,
        entity_id: str,
        limit: int = 20,
    ) -> list[TransitionRecord]:
        """Get transition history, newest first."""
        key = (installation_id, machine_id, entity_id)
        history = self._history.get(key, [])
        return list(reversed(history[-limit:]))

    def _get_machine(self, installation_id: str, machine_id: str) -> StateMachineConfig:
        key = (installation_id, machine_id)
        machine = self._machines.get(key)
        if machine is None:
            raise KeyError(f"Machine {machine_id} not found")
        return machine
