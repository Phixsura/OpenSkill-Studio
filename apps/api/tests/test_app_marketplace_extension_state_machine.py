from app.services.app_marketplace_extension_state_machine import (
    StateMachineService, StateConfig, Transition
)


def _order_machine(svc):
    """Create an order processing state machine."""
    states = [
        StateConfig("draft"),
        StateConfig("submitted"),
        StateConfig("approved"),
        StateConfig("rejected"),
        StateConfig("shipped"),
        StateConfig("delivered"),
    ]
    transitions = [
        Transition("draft", "submit", "submitted"),
        Transition("submitted", "approve", "approved",
                   guard=lambda ctx: ctx.get("total", 0) > 0),
        Transition("submitted", "reject", "rejected"),
        Transition("approved", "ship", "shipped"),
        Transition("shipped", "deliver", "delivered"),
        Transition("rejected", "resubmit", "submitted"),
    ]
    return svc.create("order-1", "draft", states, transitions)


def test_basic_transition():
    svc = StateMachineService()
    _order_machine(svc)
    result = svc.send("order-1", "submit")
    assert result["transitioned"] is True
    assert result["to"] == "submitted"
    assert svc.get_state("order-1") == "submitted"


def test_invalid_event():
    svc = StateMachineService()
    _order_machine(svc)
    result = svc.send("order-1", "deliver")  # can't deliver from draft
    assert result["transitioned"] is False
    assert "No transition" in result["error"]


def test_guard_rejects():
    svc = StateMachineService()
    _order_machine(svc)
    svc.send("order-1", "submit")
    result = svc.send("order-1", "approve")  # guard: total > 0, but no total set
    assert result["transitioned"] is False
    assert "Guard rejected" in result["error"]


def test_guard_passes():
    svc = StateMachineService()
    _order_machine(svc)
    svc.send("order-1", "submit", {"total": 100})
    result = svc.send("order-1", "approve")
    assert result["transitioned"] is True
    assert svc.get_state("order-1") == "approved"


def test_full_lifecycle():
    svc = StateMachineService()
    _order_machine(svc)
    svc.send("order-1", "submit", {"total": 50})
    svc.send("order-1", "approve")
    svc.send("order-1", "ship")
    svc.send("order-1", "deliver")
    assert svc.get_state("order-1") == "delivered"
    assert len(svc.get_history("order-1")) == 4


def test_reject_and_resubmit():
    svc = StateMachineService()
    _order_machine(svc)
    svc.send("order-1", "submit")
    svc.send("order-1", "reject")
    assert svc.get_state("order-1") == "rejected"
    svc.send("order-1", "resubmit")
    assert svc.get_state("order-1") == "submitted"


def test_on_enter_action():
    log = []
    svc = StateMachineService()
    states = [
        StateConfig("idle"),
        StateConfig("active", on_enter=lambda ctx: log.append("entered active")),
    ]
    transitions = [Transition("idle", "start", "active")]
    svc.create("m1", "idle", states, transitions)
    svc.send("m1", "start")
    assert "entered active" in log


def test_transition_action():
    svc = StateMachineService()
    states = [StateConfig("a"), StateConfig("b")]
    transitions = [Transition("a", "go", "b",
                              action=lambda ctx: ctx.update({"moved": True}))]
    svc.create("m1", "a", states, transitions)
    svc.send("m1", "go")
    assert svc.get_context("m1")["moved"] is True


def test_valid_events():
    svc = StateMachineService()
    _order_machine(svc)
    assert svc.get_valid_events("order-1") == ["submit"]
    svc.send("order-1", "submit")
    assert set(svc.get_valid_events("order-1")) == {"approve", "reject"}


def test_can_transition():
    svc = StateMachineService()
    _order_machine(svc)
    assert svc.can_transition("order-1", "submit") is True
    assert svc.can_transition("order-1", "approve") is False
