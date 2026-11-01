from app.services.app_marketplace_app_app_app_app_app_app_dashboard_complete import build_unified_dashboard

def test_dashboard():
    r = build_unified_dashboard(
        user={"name": "Alice"},
        org={"name": "Acme", "plan": "pro"},
        apps=[{"id": "a1", "name": "SuperApp", "icon": "🚀", "installs": 25000, "api_calls": 100000, "rating": 4.8}],
        notifications=5)
    assert "Alice" in r["greeting"]
    assert r["org"] == "Acme"
    assert r["health"]["overall"] == "healthy"
    assert len(r["kpis"]) == 4
    assert r["kpis"][1]["display"] == "25,000"
    assert r["notifications"] == 5
