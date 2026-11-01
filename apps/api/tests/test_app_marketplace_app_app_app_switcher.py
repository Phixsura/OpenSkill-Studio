from app.services.app_marketplace_app_app_app_switcher import build_app_switcher

def test_switcher():
    apps = [
        {"id": "a1", "name": "Auth SDK", "installs": 5000, "status": "active"},
        {"id": "a2", "name": "Charts", "installs": 3000, "status": "active"},
        {"id": "a3", "name": "Logger", "installs": 1000, "status": "paused"},
    ]
    r = build_app_switcher(apps=apps, current_app_id="a2")
    assert r["total"] == 3
    assert r["apps"][0]["current"]  # current first
    assert r["apps"][0]["id"] == "a2"
    assert r["current_app"]["name"] == "Charts"

def test_no_current():
    r = build_app_switcher(apps=[{"id": "a1", "name": "X", "installs": 0}])
    assert r["current_app"] is None
