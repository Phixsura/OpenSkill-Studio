from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_global_health_v9 import fleet_api_global_health_v9
def test_agh_v9():
    r = fleet_api_global_health_v9()
    assert r["apis_healthy"] == 600
    assert r["dora"] == "ELITE"
