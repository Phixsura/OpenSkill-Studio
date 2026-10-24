from app.services.app_developer_app_webhook_config_builder import build_webhook_config_page

def test_configured():
    p = build_webhook_config_page(app={"name": "X"}, webhook_url="https://x.com/hook", secret_configured=True,
        subscriptions=[{"event_type": "app.installed"}], delivery_stats={"success_rate": 99})
    assert p["setup_complete"] is True
    assert p["subscription_count"] == 1

def test_not_configured():
    p = build_webhook_config_page(app={"name": "X"}, webhook_url=None, secret_configured=False, subscriptions=[], delivery_stats={})
    assert p["setup_complete"] is False
    assert p["is_configured"] is False
