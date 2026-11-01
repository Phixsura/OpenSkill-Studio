from app.services.app_marketplace_notification_dispatcher import dispatch_notification, build_notification_payload, get_dispatch_stats

def test_dispatch():
    r = dispatch_notification(channels=["email", "slack"], title="Hello", message="World")
    assert r["dispatched"] == 2

def test_payload():
    p = build_notification_payload(event_type="install", app={"id": "a1", "name": "MyApp"}, details={"org": "Acme"})
    assert "MyApp" in p["title"]
    assert p["icon"] == "📥"

def test_unknown_event():
    p = build_notification_payload(event_type="custom", app={"id": "a1"}, details={})
    assert p["title"] == "custom"

def test_stats():
    dispatches = [{"dispatched": 3, "severity": "info"}, {"dispatched": 2, "severity": "error"}]
    s = get_dispatch_stats(dispatches=dispatches)
    assert s["total_dispatched"] == 5
    assert s["by_severity"]["error"] == 1
