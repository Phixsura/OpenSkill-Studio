from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_global_dashboard_v9 import fleet_api_global_dashboard_v9
def test_agd_v9():
    r = fleet_api_global_dashboard_v9()
    assert r["global"]["regions"] == 12
    assert r["dora"] == "ELITE"
    assert "NEVER STOPS" in r["status"]
