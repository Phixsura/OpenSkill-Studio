from app.services.app_marketplace_app_app_app_app_app_app_app_tab_nav import build_tabs

def test_tabs():
    r = build_tabs([
        {"id": "overview", "label": "Overview", "icon": "📊"},
        {"id": "settings", "label": "Settings", "icon": "⚙️"},
        {"id": "logs", "label": "Logs", "icon": "📋", "badge": 5},
    ], active="settings")
    assert r["count"] == 3
    assert r["active"] == "settings"
    assert r["tabs"][1]["active"]
    assert r["tabs"][2]["badge"] == 5

def test_default_active():
    r = build_tabs([{"id": "a"}, {"id": "b"}])
    assert r["tabs"][0]["active"]
