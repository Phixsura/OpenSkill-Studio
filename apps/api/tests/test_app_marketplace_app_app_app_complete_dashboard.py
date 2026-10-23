from app.services.app_marketplace_app_app_app_complete_dashboard import build_complete_dashboard

def test_dashboard():
    user = {"name": "Alice Chen"}
    org = {"name": "Acme Corp", "plan": "pro", "member_count": 5}
    apps = [
        {"id": "a1", "name": "SuperApp", "icon": "🚀", "installs": 25000, "review_count": 120, "rating": 4.8, "status": "active"},
        {"id": "a2", "name": "MiniTool", "icon": "🔧", "installs": 5000, "review_count": 30, "rating": 4.2, "status": "active"},
    ]
    r = build_complete_dashboard(user=user, org=org, apps=apps, notifications=7)
    assert "Alice" in r["greeting"]
    assert r["org"]["plan"] == "pro"
    assert len(r["quick_stats"]) == 5
    assert r["top_app"]["name"] == "SuperApp"
    assert len(r["recent_apps"]) == 2
    assert len(r["quick_actions"]) == 4
    assert r["version"] == "10.0.0"

def test_empty():
    r = build_complete_dashboard(user={"name": "Bob"}, org={"name": "X"}, apps=[])
    assert r["top_app"] is None
    assert len(r["recent_apps"]) == 0
