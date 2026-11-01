from app.services.app_marketplace_event_bus import EventBus, Event


def test_subscribe_and_publish():
    bus = EventBus()
    received = []
    bus.subscribe("user.created", lambda e: received.append(e.payload), "sub-1")
    count = bus.emit("user.created", {"user_id": "u1"})
    assert count == 1
    assert received[0]["user_id"] == "u1"


def test_multiple_subscribers():
    bus = EventBus()
    results = []
    bus.subscribe("order.placed", lambda e: results.append("A"), "a")
    bus.subscribe("order.placed", lambda e: results.append("B"), "b")
    count = bus.emit("order.placed", {"order_id": "o1"})
    assert count == 2
    assert results == ["A", "B"]


def test_unsubscribe():
    bus = EventBus()
    bus.subscribe("test.event", lambda e: None, "sub-x")
    assert bus.subscriber_count("test.event") == 1
    bus.unsubscribe("test.event", "sub-x")
    assert bus.subscriber_count("test.event") == 0


def test_dead_letter():
    bus = EventBus()
    bus.emit("no.subscribers", {"data": 1})
    dead = bus.get_dead_letters()
    assert len(dead) == 1
    assert dead[0].event_type == "no.subscribers"


def test_event_log():
    bus = EventBus()
    bus.subscribe("log.test", lambda e: None, "logger")
    bus.emit("log.test", {"a": 1})
    bus.emit("log.test", {"a": 2})
    bus.emit("other.event", {"b": 3})
    log = bus.get_event_log("log.test")
    assert len(log) == 2


def test_handler_isolation():
    bus = EventBus()
    results = []
    bus.subscribe("fail.test", lambda e: 1 / 0, "bad")  # raises
    bus.subscribe("fail.test", lambda e: results.append("ok"), "good")
    count = bus.emit("fail.test", {})
    assert count == 1  # only good handler counted
    assert results == ["ok"]


def test_clear():
    bus = EventBus()
    bus.subscribe("x", lambda e: None, "s")
    bus.emit("x", {})
    bus.clear()
    assert bus.subscriber_count("x") == 0
    assert bus.get_event_log() == []
