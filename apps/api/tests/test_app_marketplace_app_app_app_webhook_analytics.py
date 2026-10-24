from app.services.app_marketplace_app_app_app_webhook_analytics import build_webhook_analytics

def test_analytics():
    deliveries = [
        {"event_type": "app.installed", "status_code": 200, "duration_ms": 50},
        {"event_type": "app.installed", "status_code": 200, "duration_ms": 60},
        {"event_type": "app.updated", "status_code": 500, "duration_ms": 3000},
    ]
    r = build_webhook_analytics(deliveries=deliveries)
    assert r["total_deliveries"] == 3
    assert r["overall_success_rate"] == 66.7
    assert r["event_count"] == 2
    installed = next(e for e in r["events"] if e["event"] == "app.installed")
    assert installed["success_rate"] == 100.0
