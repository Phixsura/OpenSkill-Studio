from app.services.app_marketplace_app_app_app_app_app_app_app_notif_channels import get_channels, build_channel_config

def test_channels():
    assert len(get_channels()) == 5

def test_config():
    r = build_channel_config({"email": True, "slack": True, "sms": False})
    assert r["total"] == 5
    email = next(c for c in r["channels"] if c["id"] == "email")
    assert email["enabled"]
    slack = next(c for c in r["channels"] if c["id"] == "slack")
    assert slack["enabled"]
