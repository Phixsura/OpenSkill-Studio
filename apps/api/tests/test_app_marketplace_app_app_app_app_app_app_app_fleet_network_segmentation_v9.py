from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_network_segmentation_v9 import fleet_network_segmentation_v9
def test_ns2_v9():
    r = fleet_network_segmentation_v9([{"isolated": True, "policies": 10, "violations": 0}])
    assert r["violations"] == 0
    assert r["healthy"]
