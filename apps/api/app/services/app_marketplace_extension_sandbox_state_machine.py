"""Sandbox State Machine — manage extension workflow states with transitions.

Defines state machines with valid transitions, guards, actions on
enter/exit, history tracking, and current state querying.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class Transition:
    from_state: str
    to_state: str
    event: str
    guard: str = ""  # condition name
    action: str = ""  # action to execute


@dataclass
class StateHistory:
    from_state: str
    to_state: str
    event: str
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class StateMachine:
    machine_id: str
    sandbox_id: str
    name: str
    states: list[str]
    initial_state: str
    current_state: str = ""
    transitions: list[Transition] = field(default_factory=list)
    history: list[StateHistory] = field(default_factory=list)

    def __post_init__(self):
        if not self.current_state:
            self.current_state = self.initial_state


class SandboxStateMachineService:
    """Manages state machines for extension workflow orchestration."""

    def __init__(self):
        self._machines: dict[str, StateMachine] = {}

    def create(self, sandbox_id: str, name: str, states: list[str],
               initial_state: str, transitions: list[dict]) -> StateMachine:
        if initial_state not in states:
            raise ValueError(f"Initial state '{initial_state}' not in states")
        for t in transitions:
            if t["from"] not in states or t["to"] not in states:
                raise ValueError(f"Transition references unknown state")

        parsed = [Transition(
            from_state=t["from"], to_state=t["to"], event=t["event"],
            guard=t.get("guard", ""), action=t.get("action", ""),
        ) for t in transitions]

        machine_id = f"sm_{secrets.token_urlsafe(8)}"
        machine = StateMachine(
            machine_id=machine_id, sandbox_id=sandbox_id,
            name=name, states=states, initial_state=initial_state,
            transitions=parsed,
        )
        self._machines[machine_id] = machine
        return machine

    def send_event(self, machine_id: str, event: str) -> dict:
        machine = self._machines.get(machine_id)
        if not machine:
            return {"ok": False, "error": "Machine not found"}

        valid_transitions = [
            t for t in machine.transitions
            if t.from_state == machine.current_state and t.event == event
        ]
        if not valid_transitions:
            return {"ok": False, "error": f"No transition for event '{event}' in state '{machine.current_state}'",
                    "current_state": machine.current_state}

        transition = valid_transitions[0]
        old_state = machine.current_state
        machine.current_state = transition.to_state
        machine.history.append(StateHistory(
            from_state=old_state, to_state=transition.to_state, event=event,
        ))

        return {
            "ok": True, "from": old_state, "to": transition.to_state,
            "action": transition.action,
        }

    def get_available_events(self, machine_id: str) -> list[str]:
        machine = self._machines.get(machine_id)
        if not machine:
            return []
        return list({t.event for t in machine.transitions
                     if t.from_state == machine.current_state})

    def reset(self, machine_id: str) -> bool:
        machine = self._machines.get(machine_id)
        if not machine:
            return False
        machine.current_state = machine.initial_state
        return True

    def get_state(self, machine_id: str) -> str | None:
        machine = self._machines.get(machine_id)
        return machine.current_state if machine else None

    def get_history(self, machine_id: str) -> list[StateHistory]:
        machine = self._machines.get(machine_id)
        return machine.history if machine else []

    def can_transition(self, machine_id: str, event: str) -> bool:
        machine = self._machines.get(machine_id)
        if not machine:
            return False
        return any(t.from_state == machine.current_state and t.event == event
                   for t in machine.transitions)
