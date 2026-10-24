from app.services.app_marketplace_app_app_app_app_app_app_app_svc_reg_dash import build_registry_dashboard

def test_dashboard():
    r = build_registry_dashboard([
        {"name": "api", "team": "platform", "type": "service", "status": "healthy"},
        {"name": "db", "team": "data", "type": "database", "status": "healthy"},
        {"name": "worker", "team": "platform", "type": "service", "status": "degraded"},
    ])
    assert r["total"] == 3
    assert r["healthy"] == 2
    assert r["by_team"]["platform"] == 2
    assert r["by_type"]["service"] == 2
