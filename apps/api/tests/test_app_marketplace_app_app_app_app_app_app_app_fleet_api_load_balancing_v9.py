from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_load_balancing_v9 import fleet_api_load_balancing_v9
def test_alb2_v9():
    r = fleet_api_load_balancing_v9([{"algorithm": "round_robin", "rps": 50000}])
    assert r["round_robin"] == 1
    assert r["healthy"]
