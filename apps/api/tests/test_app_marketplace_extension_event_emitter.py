from app.services.app_marketplace_extension_event_emitter import EventEmitterService


def test_on_and_emit():
    ee = EventEmitterService()
    received = []
    ee.on("data", lambda x: received.append(x))
    ee.emit("data", "hello")
    ee.emit("data", "world")
    assert received == ["hello", "world"]


def test_multiple_listeners():
    ee = EventEmitterService()
    results = []
    ee.on("event", lambda: results.append("a"))
    ee.on("event", lambda: results.append("b"))
    count = ee.emit("event")
    assert count == 2
    assert results == ["a", "b"]


def test_once():
    ee = EventEmitterService()
    results = []
    ee.once("login", lambda user: results.append(user))
    ee.emit("login", "alice")
    ee.emit("login", "bob")  # listener removed
    assert results == ["alice"]


def test_off():
    ee = EventEmitterService()
    results = []
    cb = lambda x: results.append(x)
    ee.on("data", cb)
    ee.off("data", cb)
    ee.emit("data", "ignored")
    assert results == []


def test_wildcard():
    ee = EventEmitterService()
    all_events = []
    ee.on("*", lambda *args: all_events.append(args))
    ee.emit("login", "alice")
    ee.emit("logout", "alice")
    assert len(all_events) == 2


def test_priority():
    ee = EventEmitterService()
    order = []
    ee.on("event", lambda: order.append("low"), priority=1)
    ee.on("event", lambda: order.append("high"), priority=10)
    ee.emit("event")
    assert order == ["high", "low"]


def test_error_propagation():
    ee = EventEmitterService()
    errors = []
    ee.on("error", lambda err, event: errors.append((str(err), event)))
    ee.on("data", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    ee.emit("data")
    assert len(errors) == 1
    assert errors[0] == ("boom", "data")


def test_deferred():
    ee = EventEmitterService()
    results = []
    ee.on("event", lambda x: results.append(x))
    ee.emit_deferred("event", 1)
    ee.emit_deferred("event", 2)
    assert results == []  # not yet processed
    count = ee.flush_deferred()
    assert count == 2
    assert results == [1, 2]


def test_max_listeners_warning():
    ee = EventEmitterService(max_listeners=3)
    for i in range(5):
        ee.on("event", lambda: None)
    warnings = ee.get_warnings()
    assert len(warnings) >= 1
    assert "MaxListeners" in warnings[0]


def test_remove_all():
    ee = EventEmitterService()
    ee.on("a", lambda: None)
    ee.on("b", lambda: None)
    count = ee.remove_all()
    assert count == 2
    assert ee.event_names() == []


def test_emit_count():
    ee = EventEmitterService()
    ee.on("click", lambda: None)
    ee.emit("click")
    ee.emit("click")
    ee.emit("click")
    assert ee.get_emit_count("click") == 3
