from app.services.app_marketplace_app_app_app_app_app_app_app_event_bus import (
    subscribe, publish, get_subscriptions, event_history, clear_bus,
)

def test_pub_sub():
    clear_bus()
    subscribe("user.created", "send_welcome")
    subscribe("user.created", "create_profile")
    subscribe("order.placed", "process_payment")
    r = publish("user.created", {"user_id": "u1"})
    assert r["delivered_to"] == 2
    s = get_subscriptions()
    assert s["topic_count"] == 2
    assert s["total_subscriptions"] == 3
    clear_bus()

def test_history():
    clear_bus()
    publish("a", {})
    publish("b", {})
    h = event_history()
    assert len(h) == 2
    assert h[0]["topic"] == "b"
    clear_bus()
