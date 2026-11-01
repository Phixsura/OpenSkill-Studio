from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_ecosystem_health_v9 import fleet_api_ecosystem_health_v9
def test_aeh2_v9():
    r = fleet_api_ecosystem_health_v9()
    assert r["health"]["grade"] == "A+"
    assert r["health"]["dora"] == "ELITE"
    assert "NEVER STOPS" in r["status"]
