from app.services.app_marketplace_app_developer_dashboard_final import build_developer_dashboard

def test_dashboard():
    dev = {"display_name": "Alice", "verified": True, "plan": "pro"}
    apps = [
        {"name": "Auth SDK", "installs": 5000, "revenue": 2500, "rating": 4.5, "status": "active"},
        {"name": "Charts", "installs": 3000, "revenue": 1500, "rating": 4.2, "status": "active"},
    ]
    analytics = {"dau": 500, "wau": 2000, "mau": 5000, "api_calls_today": 15000, "error_rate": 0.1}
    r = build_developer_dashboard(developer=dev, apps=apps, analytics=analytics, notifications=5)
    assert r["developer"]["name"] == "Alice"
    assert r["developer"]["verified"]
    assert r["overview"]["total_apps"] == 2
    assert r["overview"]["total_installs"] == 8000
    assert r["overview"]["total_revenue"] == 4000
    assert r["top_app"]["name"] == "Auth SDK"
    assert r["analytics"]["dau"] == 500
    assert len(r["quick_actions"]) == 4

def test_empty():
    r = build_developer_dashboard(developer={}, apps=[], analytics={}, notifications=0)
    assert r["overview"]["total_apps"] == 0
    assert r["top_app"] is None
