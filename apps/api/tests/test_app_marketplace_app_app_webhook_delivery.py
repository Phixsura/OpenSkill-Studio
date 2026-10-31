from app.services.app_marketplace_app_app_webhook_delivery import record_delivery, build_delivery_stats

def test_record():
    r = record_delivery(webhook_id="wh1", url="https://example.com/hook",
                        event_type="app.installed", status_code=200, duration_ms=85)
    assert r["id"].startswith("dlv_")
    assert r["success"]

def test_stats():
    deliveries = [
        {"event_type": "app.installed", "success": True, "duration_ms": 50},
        {"event_type": "app.installed", "success": True, "duration_ms": 70},
        {"event_type": "app.updated", "success": False, "duration_ms": 3000},
    ]
    r = build_delivery_stats(deliveries=deliveries)
    assert r["success_rate"] == 66.7
    assert r["by_event"]["app.installed"] == 2
