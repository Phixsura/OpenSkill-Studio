from app.services.app_marketplace_complete_webhook_management import build_complete_webhook_management

def test_page():
    p = build_complete_webhook_management(
        webhooks=[{"url": "https://x.com/hook", "active": True}, {"url": "https://y.com/hook", "active": False}],
        delivery_stats={"success_rate": 95.5}, recent_attempts=[{"status": 200}],
        event_types=["app.installed", "app.updated"])
    assert p["page_type"] == "webhook_management"
    assert p["overview"]["active"] == 1
    assert len(p["sections"]) == 4
