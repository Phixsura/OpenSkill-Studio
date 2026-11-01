from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dash_v5 import fleet_ai_dashboard_v5
def test_dv5():
    r = fleet_ai_dashboard_v5([{"active": True, "widgets": 500, "users_24h": 50000, "custom_views": 200}])
    assert r["widgets"] == 500
    assert r["popular"]
