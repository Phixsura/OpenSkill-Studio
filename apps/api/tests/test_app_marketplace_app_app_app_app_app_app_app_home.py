from app.services.app_marketplace_app_app_app_app_app_app_app_home import build_app_home

def test_home():
    app = {"name": "SuperApp", "icon": "🚀", "version": "2.0.0", "status": "active", "published": True}
    stats = {"installs": 25000, "api_calls": 100000, "rating": 4.7, "reviews": 120}
    activity = [{"action": "Deployed v2.0.0", "timestamp": "2026-10-01T10:00:00Z"}]
    r = build_app_home(app=app, stats=stats, recent_activity=activity, has_update=True)
    assert r["header"]["name"] == "SuperApp"
    assert r["quick_stats"][0]["display"] == "25,000"
    assert r["has_update"]
    assert len(r["quick_links"]) == 4
    assert len(r["recent_activity"]) == 1
