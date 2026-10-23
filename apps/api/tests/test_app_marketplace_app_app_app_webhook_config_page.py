from app.services.app_marketplace_app_app_app_webhook_config_page import build_webhook_config_page

def test_config():
    webhooks = [
        {"id": "wh1", "url": "https://a.com/hook", "events": ["app.installed"], "active": True, "success_rate": 98.5},
        {"id": "wh2", "url": "https://b.com/hook", "events": ["deploy.completed", "deploy.failed"], "active": False},
    ]
    r = build_webhook_config_page(webhooks=webhooks)
    assert r["total"] == 2
    assert r["active"] == 1
    assert r["total_event_types"] == 9
    assert r["can_add"]
