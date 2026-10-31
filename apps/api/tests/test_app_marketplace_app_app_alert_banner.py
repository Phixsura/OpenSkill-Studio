from app.services.app_marketplace_app_app_alert_banner import build_alert

def test_info():
    r = build_alert(message="New version available", title="Update")
    assert r["icon"] == "ℹ️"
    assert r["title"] == "Update"
    assert r["dismissible"]

def test_error():
    r = build_alert(message="Deploy failed", variant="error", dismissible=False)
    assert r["icon"] == "❌"
    assert not r["dismissible"]

def test_with_action():
    r = build_alert(message="Update available", action={"label": "Update Now", "url": "/update"})
    assert r["action"]["label"] == "Update Now"
