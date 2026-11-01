from app.services.app_marketplace_app_app_webhook_setup_wizard import start_webhook_setup, list_available_events

def test_setup():
    r = start_webhook_setup(url="https://example.com/hook", events=["app.installed", "deploy.completed"])
    assert r["webhook_id"].startswith("wh_")
    assert r["secret"].startswith("whsec_")
    assert r["setup_complete"]

def test_http_rejected():
    r = start_webhook_setup(url="http://insecure.com", events=["app.installed"])
    assert "error" in r

def test_invalid_event():
    r = start_webhook_setup(url="https://x.com/hook", events=["invalid.event"])
    assert "error" in r

def test_list_events():
    r = list_available_events()
    assert r["total"] == 7
    assert "App" in r["categories"]
