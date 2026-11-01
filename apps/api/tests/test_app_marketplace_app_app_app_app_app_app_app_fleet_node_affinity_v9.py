from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_node_affinity_v9 import fleet_node_affinity_v9
def test_na_v9():
    r = fleet_node_affinity_v9([{"type": "required", "violated": False}])
    assert r["violations"] == 0
    assert r["healthy"]
