"""Tests for App State Machine — define, transitions, events, history."""

import pytest

from app.services.app_state_machine import AppStateMachine

STATES = ["draft", "review", "approved", "rejected"]
TRANSITIONS = [
    {"from": "draft", "to": "review", "event": "submit"},
    {"from": "review", "to": "approved", "event": "approve"},
    {"from": "review", "to": "rejected", "event": "reject"},
    {"from": "rejected", "to": "draft", "event": "revise"},
]


class TestDefineMachine:
    def test_define(self):
        sm = AppStateMachine()
        m = sm.define_machine("inst-1", "approval", "draft", STATES, TRANSITIONS)
        assert m.machine_id == "approval"
        assert m.initial_state == "draft"
        assert len(m.transitions) == 4

    def test_duplicate(self):
        sm = AppStateMachine()
        sm.define_machine("inst-1", "m1", "draft", STATES, TRANSITIONS)
        with pytest.raises(ValueError, match="already exists"):
            sm.define_machine("inst-1", "m1", "draft", STATES, TRANSITIONS)

    def test_too_few_states(self):
        sm = AppStateMachine()
        with pytest.raises(ValueError, match="2 states"):
            sm.define_machine("inst-1", "m1", "a", ["a"], [])

    def test_invalid_initial_state(self):
        sm = AppStateMachine()
        with pytest.raises(ValueError, match="Initial state"):
            sm.define_machine("inst-1", "m1", "unknown", ["a", "b"], [])

    def test_invalid_transition_state(self):
        sm = AppStateMachine()
        with pytest.raises(ValueError, match="from_state"):
            sm.define_machine("inst-1", "m1", "a", ["a", "b"],
                              [{"from": "x", "to": "b", "event": "go"}])


class TestGetState:
    def test_initial_state(self):
        sm = AppStateMachine()
        sm.define_machine("inst-1", "m1", "draft", STATES, TRANSITIONS)
        assert sm.get_state("inst-1", "m1", "entity-1") == "draft"


class TestSendEvent:
    def test_transition(self):
        sm = AppStateMachine()
        sm.define_machine("inst-1", "m1", "draft", STATES, TRANSITIONS)
        new = sm.send_event("inst-1", "m1", "entity-1", "submit")
        assert new == "review"
        assert sm.get_state("inst-1", "m1", "entity-1") == "review"

    def test_full_flow(self):
        sm = AppStateMachine()
        sm.define_machine("inst-1", "m1", "draft", STATES, TRANSITIONS)
        sm.send_event("inst-1", "m1", "e1", "submit")
        sm.send_event("inst-1", "m1", "e1", "approve")
        assert sm.get_state("inst-1", "m1", "e1") == "approved"

    def test_reject_and_revise(self):
        sm = AppStateMachine()
        sm.define_machine("inst-1", "m1", "draft", STATES, TRANSITIONS)
        sm.send_event("inst-1", "m1", "e1", "submit")
        sm.send_event("inst-1", "m1", "e1", "reject")
        sm.send_event("inst-1", "m1", "e1", "revise")
        assert sm.get_state("inst-1", "m1", "e1") == "draft"

    def test_invalid_event(self):
        sm = AppStateMachine()
        sm.define_machine("inst-1", "m1", "draft", STATES, TRANSITIONS)
        with pytest.raises(ValueError, match="No transition"):
            sm.send_event("inst-1", "m1", "e1", "approve")  # can't approve from draft


class TestAvailableEvents:
    def test_from_draft(self):
        sm = AppStateMachine()
        sm.define_machine("inst-1", "m1", "draft", STATES, TRANSITIONS)
        events = sm.get_available_events("inst-1", "m1", "e1")
        assert events == ["submit"]

    def test_from_review(self):
        sm = AppStateMachine()
        sm.define_machine("inst-1", "m1", "draft", STATES, TRANSITIONS)
        sm.send_event("inst-1", "m1", "e1", "submit")
        events = sm.get_available_events("inst-1", "m1", "e1")
        assert set(events) == {"approve", "reject"}


class TestHistory:
    def test_history(self):
        sm = AppStateMachine()
        sm.define_machine("inst-1", "m1", "draft", STATES, TRANSITIONS)
        sm.send_event("inst-1", "m1", "e1", "submit", now=1000.0)
        sm.send_event("inst-1", "m1", "e1", "approve", now=1001.0)
        h = sm.get_history("inst-1", "m1", "e1")
        assert len(h) == 2
        assert h[0].to_state == "approved"  # newest first
        assert h[1].to_state == "review"


class TestEntityIsolation:
    def test_independent_entities(self):
        sm = AppStateMachine()
        sm.define_machine("inst-1", "m1", "draft", STATES, TRANSITIONS)
        sm.send_event("inst-1", "m1", "e1", "submit")
        assert sm.get_state("inst-1", "m1", "e2") == "draft"


class TestInstallationIsolation:
    def test_cross_installation(self):
        sm = AppStateMachine()
        sm.define_machine("inst-1", "m1", "draft", STATES, TRANSITIONS)
        with pytest.raises(KeyError):
            sm.get_state("inst-2", "m1", "e1")
