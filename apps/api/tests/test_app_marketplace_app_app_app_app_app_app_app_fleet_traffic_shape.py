from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_traffic_shape import fleet_traffic_shaping
def test_shaping():
    r = fleet_traffic_shaping([{"weight": 80}, {"weight": 20}])
    assert r["active"] == 2
    assert r["total_weight"] == 100
    assert not r["balanced"]
