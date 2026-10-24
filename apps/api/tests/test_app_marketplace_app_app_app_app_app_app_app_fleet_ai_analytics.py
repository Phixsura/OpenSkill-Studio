from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_analytics import fleet_ai_analytics
def test_aa():
    r = fleet_ai_analytics([{"active": True, "metrics": 200, "views_24h": 50000}])
    assert r["metrics"] == 200
    assert r["adopted"]
