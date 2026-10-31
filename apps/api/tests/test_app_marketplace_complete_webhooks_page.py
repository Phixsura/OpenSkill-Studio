from app.services.app_marketplace_complete_webhooks_page import build_complete_webhooks_page

def test_page():
    p = build_complete_webhooks_page(
        app={"id": "a1", "name": "App"},
        endpoints=[{"url": "https://x.com", "active": True}, {"url": "https://y.com", "active": False}],
        deliveries=[{"success": True}, {"success": True}, {"success": False}],
        event_types=["install", "update", "review"],
        retry_policy={"max_retries": 5})
    assert p["overview"]["active"] == 1
    assert p["overview"]["delivery_rate"] > 60
    assert len(p["tabs"]) == 5
    assert len(p["available_events"]) == 3
