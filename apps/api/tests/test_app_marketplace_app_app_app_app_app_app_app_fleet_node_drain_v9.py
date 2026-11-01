from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_node_drain_v9 import fleet_node_drain_v9
def test_nd_v9():
    r = fleet_node_drain_v9([{"cordoned": False, "draining": False, "drained": False}])
    assert r["draining"] == 0
    assert r["healthy"]
