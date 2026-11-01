from app.services.app_marketplace_extension_sandbox_state_machine import (
    SandboxStateMachineService,
)
import pytest


ORDER_STATES = ["draft", "submitted", "processing", "shipped", "delivered", "cancelled"]
ORDER_TRANSITIONS = [
    {"from": "draft", "to": "submitted", "event": "submit"},
    {"from": "submitted", "to": "processing", "event": "process"},
    {"from": "processing", "to": "shipped", "event": "ship"},
    {"from": "shipped", "to": "delivered", "event": "deliver"},
    {"from": "draft", "to": "cancelled", "event": "cancel"},
    {"from": "submitted", "to": "cancelled", "event": "cancel"},
]


def test_create():
    svc = SandboxStateMachineService()
    sm = svc.create("sb-1", "order", ORDER_STATES, "draft", ORDER_TRANSITIONS)
    assert sm.current_state == "draft"


def test_send_event():
    svc = SandboxStateMachineService()
    sm = svc.create("sb-1", "order", ORDER_STATES, "draft", ORDER_TRANSITIONS)
    result = svc.send_event(sm.machine_id, "submit")
    assert result["ok"] is True
    assert result["to"] == "submitted"
    assert svc.get_state(sm.machine_id) == "submitted"


def test_invalid_event():
    svc = SandboxStateMachineService()
    sm = svc.create("sb-1", "order", ORDER_STATES, "draft", ORDER_TRANSITIONS)
    result = svc.send_event(sm.machine_id, "deliver")
    assert result["ok"] is False


def test_full_workflow():
    svc = SandboxStateMachineService()
    sm = svc.create("sb-1", "order", ORDER_STATES, "draft", ORDER_TRANSITIONS)
    for event in ["submit", "process", "ship", "deliver"]:
        svc.send_event(sm.machine_id, event)
    assert svc.get_state(sm.machine_id) == "delivered"
    assert len(svc.get_history(sm.machine_id)) == 4


def test_available_events():
    svc = SandboxStateMachineService()
    sm = svc.create("sb-1", "order", ORDER_STATES, "draft", ORDER_TRANSITIONS)
    events = svc.get_available_events(sm.machine_id)
    assert set(events) == {"submit", "cancel"}


def test_can_transition():
    svc = SandboxStateMachineService()
    sm = svc.create("sb-1", "order", ORDER_STATES, "draft", ORDER_TRANSITIONS)
    assert svc.can_transition(sm.machine_id, "submit") is True
    assert svc.can_transition(sm.machine_id, "ship") is False


def test_reset():
    svc = SandboxStateMachineService()
    sm = svc.create("sb-1", "order", ORDER_STATES, "draft", ORDER_TRANSITIONS)
    svc.send_event(sm.machine_id, "submit")
    svc.reset(sm.machine_id)
    assert svc.get_state(sm.machine_id) == "draft"


def test_invalid_initial_state():
    svc = SandboxStateMachineService()
    with pytest.raises(ValueError, match="Initial state"):
        svc.create("sb-1", "order", ["a", "b"], "unknown", [])


def test_cancel_from_submitted():
    svc = SandboxStateMachineService()
    sm = svc.create("sb-1", "order", ORDER_STATES, "draft", ORDER_TRANSITIONS)
    svc.send_event(sm.machine_id, "submit")
    result = svc.send_event(sm.machine_id, "cancel")
    assert result["ok"] is True
    assert svc.get_state(sm.machine_id) == "cancelled"
