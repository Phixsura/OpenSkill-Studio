from app.services.app_marketplace_extension_vector_clock import (
    VectorClock, VectorClockService
)


def test_increment():
    vc = VectorClock("A")
    vc.increment()
    vc.increment()
    assert vc.get("A") == 2


def test_merge():
    a = VectorClock("A")
    a.increment()  # A:1
    b = VectorClock("B")
    b.increment()
    b.increment()  # B:2
    a.merge(b)  # A:1, B:2
    assert a.get("A") == 1
    assert a.get("B") == 2


def test_happens_before():
    a = VectorClock.from_dict({"A": 1, "B": 0})
    b = VectorClock.from_dict({"A": 1, "B": 1})
    assert a.happens_before(b) is True
    assert b.happens_before(a) is False


def test_concurrent():
    a = VectorClock.from_dict({"A": 2, "B": 1})
    b = VectorClock.from_dict({"A": 1, "B": 2})
    assert a.concurrent_with(b) is True
    assert a.compare(b) == "concurrent"


def test_equal():
    a = VectorClock.from_dict({"A": 1, "B": 2})
    b = VectorClock.from_dict({"A": 1, "B": 2})
    assert a.equals(b) is True
    assert a.compare(b) == "equal"


def test_compare_after():
    a = VectorClock.from_dict({"A": 2, "B": 1})
    b = VectorClock.from_dict({"A": 1, "B": 0})
    assert a.compare(b) == "after"


def test_service_message_flow():
    svc = VectorClockService()
    svc.register_node("A")
    svc.register_node("B")
    # A does local event
    svc.local_event("A")  # A:{A:1}
    # A sends message to B
    msg_clock = svc.send_message("A")  # A:{A:2}
    # B receives
    svc.receive_message("B", msg_clock)  # B:{A:2, B:1}
    b_state = svc._node_clocks["B"]
    assert b_state.get("A") == 2
    assert b_state.get("B") == 1


def test_causal_ordering():
    svc = VectorClockService()
    svc.register_node("A")
    svc.register_node("B")
    svc.register_node("C")
    e1 = svc.local_event("A")  # A:1
    msg = svc.send_message("A")  # A:2
    e2 = svc.receive_message("B", msg)  # A:2, B:1
    assert svc.compare_events(e1, e2) == "before"


def test_concurrent_events():
    svc = VectorClockService()
    svc.register_node("A")
    svc.register_node("B")
    e_a = svc.local_event("A")  # A:{A:1}
    e_b = svc.local_event("B")  # B:{B:1}
    assert svc.compare_events(e_a, e_b) == "concurrent"


def test_serialization():
    vc = VectorClock("A")
    vc.increment()
    vc.increment()
    data = vc.to_dict()
    restored = VectorClock.from_dict(data, "A")
    assert restored.equals(vc)
