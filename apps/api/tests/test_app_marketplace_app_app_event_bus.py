from app.services.app_marketplace_app_app_event_bus import EventBus

def test_pub_sub():
    bus = EventBus()
    bus.subscribe(event="app.installed", handler_id="h1", name="Logger")
    r = bus.publish(event="app.installed", payload={"app_id": "a1"})
    assert r["subscriber_count"] == 1

def test_no_subscribers():
    bus = EventBus()
    r = bus.publish(event="unknown")
    assert r["subscriber_count"] == 0

def test_list():
    bus = EventBus()
    bus.subscribe(event="e1", handler_id="h1")
    bus.subscribe(event="e2", handler_id="h2")
    r = bus.list_subscriptions()
    assert r["total"] == 2
    assert len(r["event_types"]) == 2

def test_history():
    bus = EventBus()
    bus.publish(event="a")
    bus.publish(event="b")
    r = bus.history(limit=10)
    assert r["total"] == 2
    assert r["events"][0]["event"] == "b"  # newest first
