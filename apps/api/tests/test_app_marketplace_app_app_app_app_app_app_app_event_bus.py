from app.services.app_marketplace_app_app_app_app_app_app_app_event_bus import EventBus

def test_pubsub():
    bus = EventBus()
    bus.subscribe("user.created", subscriber="email_service")
    bus.subscribe("user.created", subscriber="analytics")
    bus.subscribe("order.placed", subscriber="inventory")
    r = bus.publish("user.created", payload={"user_id": "u1"})
    assert r["delivered_to"] == 2
    assert "email_service" in r["subscribers"]
    bus.unsubscribe("user.created", subscriber="email_service")
    r2 = bus.publish("user.created", payload={"user_id": "u2"})
    assert r2["delivered_to"] == 1
    s = bus.stats()
    assert s["topics"] == 2
    assert s["published"] == 2
    assert s["delivered"] == 3
