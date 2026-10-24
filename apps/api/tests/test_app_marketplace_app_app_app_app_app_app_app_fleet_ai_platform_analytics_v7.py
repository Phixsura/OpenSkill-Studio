from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_analytics_v7 import fleet_ai_analytics_v7
def test_av7():
    r = fleet_ai_analytics_v7([{"active": True, "events": 10000000000, "insights": 1000, "reports": 500}])
    assert r["events"] == 10000000000
    assert r["data_driven"]
