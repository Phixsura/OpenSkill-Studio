from app.services.app_marketplace_app_app_webhook_log import build_webhook_log

def test_log():
    deliveries = [
        {"id": "1", "event": "app.installed", "url": "https://example.com/hook",
         "status_code": 200, "duration_ms": 150, "timestamp": "2026-01-02T00:00:00Z"},
        {"id": "2", "event": "app.updated", "url": "https://example.com/hook",
         "status_code": 500, "duration_ms": 3000, "timestamp": "2026-01-01T00:00:00Z"},
    ]
    r = build_webhook_log(deliveries=deliveries)
    assert r["total"] == 2
    assert r["success"] == 1
    assert r["failed"] == 1
    assert r["success_rate"] == 50.0
    assert r["deliveries"][0]["id"] == "1"  # newest first

def test_empty():
    r = build_webhook_log(deliveries=[])
    assert r["success_rate"] == 0
