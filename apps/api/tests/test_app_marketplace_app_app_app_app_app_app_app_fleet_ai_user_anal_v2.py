from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_user_anal_v2 import fleet_ai_user_analytics_v2
def test_uav2():
    r = fleet_ai_user_analytics_v2([{"active": True, "dau": 500000, "mau": 2000000, "retention_pct": 85, "engagement_min": 25}])
    assert r["dau"] == 500000
    assert r["growing"]
