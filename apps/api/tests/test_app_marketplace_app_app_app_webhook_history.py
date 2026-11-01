from app.services.app_marketplace_app_app_app_webhook_history import build_webhook_history

def test_history():
    deliveries = [
        {"event_type": "app.installed", "status_code": 200, "duration_ms": 50},
        {"event_type": "app.installed", "status_code": 200, "duration_ms": 60},
        {"event_type": "app.updated", "status_code": 500, "duration_ms": 3000},
    ]
    r = build_webhook_history(deliveries=deliveries)
    assert r["total"] == 3
    assert r["success"] == 2
    assert r["success_rate"] == 66.7
    assert r["top_event"] == "app.installed"

def test_empty():
    r = build_webhook_history(deliveries=[])
    assert r["total"] == 0
