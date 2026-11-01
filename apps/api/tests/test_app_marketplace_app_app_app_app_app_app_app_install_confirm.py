from app.services.app_marketplace_app_app_app_app_app_app_app_install_confirm import build_install_confirmation

def test_confirm():
    r = build_install_confirmation(
        app_name="Slack Bot", app_icon="💬", version="2.1.0",
        permissions_granted=["read:profile", "webhooks"],
        webhook_url="https://hooks.slack.com/test")
    assert r["app_name"] == "Slack Bot"
    assert r["status"] == "installed"
    assert r["permission_count"] == 2
    assert r["webhook_configured"]
    assert len(r["next_steps"]) == 3
