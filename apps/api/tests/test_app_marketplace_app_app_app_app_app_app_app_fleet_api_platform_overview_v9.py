from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_platform_overview_v9 import fleet_api_platform_overview_v9
def test_apo_v9():
    r = fleet_api_platform_overview_v9()
    assert r["health"]["grade"] == "A+"
    assert r["dora"]["overall"] == "ELITE"
    assert r["overview"]["platform_modules"] == 10
    assert "NEVER STOPS" in r["status"]
