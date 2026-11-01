from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_container_network_v9 import fleet_container_network_v9
def test_cn2_v9():
    r = fleet_container_network_v9([{"healthy": True, "pods": 500, "network_policies": 50}])
    assert r["pods_networked"] == 500
    assert r["all_healthy"]
