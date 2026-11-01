from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_traffic_dashboard_v9 import fleet_api_traffic_dashboard_v9
def test_atd3_v9():
    r = fleet_api_traffic_dashboard_v9()
    assert r["traffic"]["total_rps"] == 1000000
    assert "HEALTHY" in r["status"]
