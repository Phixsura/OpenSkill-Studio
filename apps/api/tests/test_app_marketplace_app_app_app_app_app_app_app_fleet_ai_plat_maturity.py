from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_maturity import fleet_ai_platform_maturity
def test_pm():
    r = fleet_ai_platform_maturity([{"active": True, "level": 5, "dimensions": 20, "score": 95}])
    assert r["level"] == 5
    assert r["mature"]
