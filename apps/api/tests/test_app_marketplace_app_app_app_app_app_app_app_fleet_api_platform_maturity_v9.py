from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_platform_maturity_v9 import fleet_api_platform_maturity_v9
def test_apm2_v9():
    r = fleet_api_platform_maturity_v9()
    assert r["maturity_level"] == 5
    assert r["grade"] == "A+"
