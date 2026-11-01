from app.services.app_marketplace_app_app_app_app_app_webhooks_page import build_webhooks_page

def test_page():
    webhooks = [{"id": "wh1", "url": "https://a.com/hook", "events": ["app.installed"], "active": True, "success_rate": 98}]
    deliveries = [{"success": True}, {"success": True}, {"success": False}]
    r = build_webhooks_page(app_name="SuperApp", webhooks=webhooks, recent_deliveries=deliveries)
    assert r["app_name"] == "SuperApp"
    assert r["active"] == 1
    assert r["delivery_stats"]["success_rate"] == 66.7
    assert r["health"] == "critical"
