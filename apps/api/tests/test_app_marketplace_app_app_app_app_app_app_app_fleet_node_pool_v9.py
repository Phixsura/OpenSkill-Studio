from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_node_pool_v9 import fleet_node_pool_v9
def test_np2_v9():
    r = fleet_node_pool_v9([{"status": "ready", "scaling": False, "nodes": 20}])
    assert r["total_nodes"] == 20
    assert r["healthy"]
