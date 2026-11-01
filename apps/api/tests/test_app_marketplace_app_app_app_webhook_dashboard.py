from app.services.app_marketplace_app_app_app_webhook_dashboard import build_webhook_dashboard

def test_dashboard():
    eps = [{"url": "https://a.com/hook", "active": True, "events": ["app.installed"]}]
    deliveries = [
        {"status_code": 200}, {"status_code": 200}, {"status_code": 500},
    ]
    r = build_webhook_dashboard(endpoints=eps, recent_deliveries=deliveries)
    assert r["active_endpoints"] == 1
    assert r["deliveries"]["success_rate"] == 66.7
    assert r["health"] == "critical"
