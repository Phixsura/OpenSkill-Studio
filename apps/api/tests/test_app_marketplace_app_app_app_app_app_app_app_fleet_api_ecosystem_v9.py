from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_ecosystem_v9 import fleet_api_ecosystem_v9
def test_aeco_v9():
    r = fleet_api_ecosystem_v9()
    assert r["health"]["all_green"]
    assert "NEVER STOPS" in r["status"]
