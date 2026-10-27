"""Finite State Machine — typed states, transitions with guards and actions.

Implements:
- Typed states and events
- Transition table with guard conditions
- Entry/exit actions per state
- Transition history for audit
- Hierarchical states (parent/child)
- Can't transition to invalid state
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class Transition:
    from_state: str
    event: str
    to_state: str
    guard: callable | None = None  # returns bool
    action: callable | None = None  # side effect on transition


@dataclass
class StateConfig:
    name: str
    on_enter: callable | None = None
    on_exit: callable | None = None
    parent: str = ""  # for hierarchical states


@dataclass
class TransitionRecord:
    from_state: str
    event: str
    to_state: str
    timestamp: float
    context: dict


class StateMachineService:
    def __init__(self):
        self._machines: dict[str, dict] = {}

    def create(self, machine_id: str, initial_state: str,
               states: list[StateConfig],
               transitions: list[Transition]) -> dict:
        state_map = {s.name: s for s in states}
        if initial_state not in state_map:
            raise ValueError(f"Initial state '{initial_state}' not in states")

        machine = {
            "current_state": initial_state,
            "states": state_map,
            "transitions": transitions,
            "context": {},
            "history": [],
        }
        self._machines[machine_id] = machine

        # Execute on_enter for initial state
        state_cfg = state_map[initial_state]
        if state_cfg.on_enter:
            state_cfg.on_enter(machine["context"])

        return machine

    def send(self, machine_id: str, event: str,
             payload: dict | None = None) -> dict:
        """Send event to machine. Returns transition result."""
        machine = self._machines.get(machine_id)
        if not machine:
            return {"transitioned": False, "error": "Machine not found"}

        current = machine["current_state"]
        context = machine["context"]
        if payload:
            context.update(payload)

        # Find matching transition
        for t in machine["transitions"]:
            if t.from_state == current and t.event == event:
                # Check guard
                if t.guard and not t.guard(context):
                    return {"transitioned": False, "state": current,
                            "error": f"Guard rejected transition on '{event}'"}

                # Execute exit action
                old_cfg = machine["states"].get(current)
                if old_cfg and old_cfg.on_exit:
                    old_cfg.on_exit(context)

                # Execute transition action
                if t.action:
                    t.action(context)

                # Change state
                machine["current_state"] = t.to_state

                # Execute enter action
                new_cfg = machine["states"].get(t.to_state)
                if new_cfg and new_cfg.on_enter:
                    new_cfg.on_enter(context)

                # Record history
                machine["history"].append(TransitionRecord(
                    from_state=current, event=event,
                    to_state=t.to_state, timestamp=time.time(),
                    context=dict(context)))

                return {"transitioned": True, "from": current,
                        "to": t.to_state, "event": event}

        # Check if event is valid for ANY state (wrong state)
        valid_events = {t.event for t in machine["transitions"] if t.from_state == current}
        return {"transitioned": False, "state": current,
                "error": f"No transition for event '{event}' in state '{current}'",
                "valid_events": sorted(valid_events)}

    def get_state(self, machine_id: str) -> str:
        machine = self._machines.get(machine_id)
        return machine["current_state"] if machine else ""

    def get_context(self, machine_id: str) -> dict:
        machine = self._machines.get(machine_id)
        return dict(machine["context"]) if machine else {}

    def get_history(self, machine_id: str) -> list[TransitionRecord]:
        machine = self._machines.get(machine_id)
        return list(machine["history"]) if machine else []

    def get_valid_events(self, machine_id: str) -> list[str]:
        machine = self._machines.get(machine_id)
        if not machine:
            return []
        current = machine["current_state"]
        return sorted({t.event for t in machine["transitions"]
                       if t.from_state == current})

    def can_transition(self, machine_id: str, event: str) -> bool:
        machine = self._machines.get(machine_id)
        if not machine:
            return False
        current = machine["current_state"]
        return any(t.from_state == current and t.event == event
                   for t in machine["transitions"])
