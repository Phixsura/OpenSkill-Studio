from app.services.app_marketplace_app_app_app_app_app_app_app_event_bus import EventBus

def test_pubsub():
    bus = EventBus()
    bus.subscribe("order.created", "email-handler")
    bus.subscribe("order.created", "analytics-handler")
    r = bus.publish("order.created", {"order_id": "o1"})
    assert r["delivered"] == 2
    s = bus.stats()
    assert s["published"] == 1
    assert s["delivered"] == 2

def test_filter():
    bus = EventBus()
    bus.subscribe("order.created", "vip-handler", filter_fn=lambda p: p.get("amount", 0) > 1000)
    r = bus.publish("order.created", {"amount": 500})
    assert r["delivered"] == 0
    r2 = bus.publish("order.created", {"amount": 2000})
    assert r2["delivered"] == 1
