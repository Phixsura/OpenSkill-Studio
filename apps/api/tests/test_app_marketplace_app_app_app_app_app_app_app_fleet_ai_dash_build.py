from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dash_build import fleet_ai_dashboard_builder
def test_db():
    r = fleet_ai_dashboard_builder([{"active": True, "dashboards": 500, "panels": 5000, "viewers_24h": 10000}])
    assert r["dashboards"] == 500
    assert r["popular"]
