from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_traffic_shift import fleet_traffic_shift
def test_shift():
    r = fleet_traffic_shift([{"name": "v2", "weight": 80}, {"name": "v1", "weight": 20}])
    assert r["primary"] == "v2"
    assert r["primary_pct"] == 80.0
