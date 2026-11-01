from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_topology_map_v9 import fleet_topology_map_v9
def test_tm_v9():
    r = fleet_topology_map_v9([{"type": "compute", "connections": 5}, {"type": "storage", "connections": 3}])
    assert r["compute"] == 1
    assert r["connections"] == 8
    assert r["healthy"]
