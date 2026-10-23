from app.services.app_marketplace_app_app_app_webhook_logs_page import build_webhook_logs_page

def test_logs():
    deliveries = [
        {"id": "d1", "event_type": "app.installed", "url": "https://x.com", "status_code": 200, "duration_ms": 50},
        {"id": "d2", "event_type": "app.updated", "url": "https://x.com", "status_code": 500, "duration_ms": 3000},
    ]
    r = build_webhook_logs_page(deliveries=deliveries)
    assert r["total"] == 2
    assert r["success"] == 1
    assert r["success_rate"] == 50.0
    assert len(r["deliveries"]) == 2
