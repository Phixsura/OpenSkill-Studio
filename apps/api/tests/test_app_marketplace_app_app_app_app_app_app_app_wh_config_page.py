from app.services.app_marketplace_app_app_app_app_app_app_app_wh_config_page import build_webhook_config

def test_config():
    r = build_webhook_config([
        {"id": "wh1", "url": "https://example.com/hook", "events": ["app.installed", "app.updated"], "active": True, "success_rate": 98.5},
        {"id": "wh2", "url": "https://other.com/hook", "events": ["user.created"], "active": False, "success_rate": 100},
    ])
    assert r["total"] == 2
    assert r["active"] == 1
    assert r["all_secure"]
    assert r["webhooks"][0]["event_count"] == 2
