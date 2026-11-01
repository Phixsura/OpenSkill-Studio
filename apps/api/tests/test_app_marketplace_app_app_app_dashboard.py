from app.services.app_marketplace_app_app_app_dashboard import build_dashboard

def test_dashboard():
    apps = [{"id": "a1", "name": "SuperApp", "icon": "🚀", "status": "active", "downloads": 5000}]
    r = build_dashboard(user_name="Alice", apps=apps, notifications=3, recent_deploys=2, open_tickets=1)
    assert "Alice" in r["greeting"]
    assert r["has_apps"]
    assert len(r["quick_stats"]) == 4
    assert r["recent_apps"][0]["name"] == "SuperApp"

def test_empty():
    r = build_dashboard(user_name="Bob", apps=[])
    assert not r["has_apps"]
