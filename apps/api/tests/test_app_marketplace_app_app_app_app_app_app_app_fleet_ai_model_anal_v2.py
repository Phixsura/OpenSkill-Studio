from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_anal_v2 import fleet_ai_model_analytics_v2
def test_mav2():
    r = fleet_ai_model_analytics_v2([{"active": True, "models": 500, "dau": 100000, "requests_24h": 1000000000, "revenue_usd": 100000}])
    assert r["dau"] == 100000
    assert r["growing"]
