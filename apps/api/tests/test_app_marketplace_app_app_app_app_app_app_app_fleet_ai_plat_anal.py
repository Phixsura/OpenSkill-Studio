from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_anal import fleet_ai_platform_analytics
def test_pa():
    r = fleet_ai_platform_analytics([{"active": True, "dau": 100000, "mau": 500000, "api_calls_24h": 1000000000, "revenue_usd": 100000}])
    assert r["dau"] == 100000
    assert r["growing"]
