from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_operational_health_v9 import fleet_api_operational_health_v9
def test_aoh_v9():
    r = fleet_api_operational_health_v9()
    assert r["health"]["healthy"] == 600
    assert r["dora"] == "ELITE"
