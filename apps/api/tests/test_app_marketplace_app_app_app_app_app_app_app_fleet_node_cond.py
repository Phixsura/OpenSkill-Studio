from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_node_cond import fleet_node_conditions
def test_nodes():
    r = fleet_node_conditions([{"ready": True}, {"ready": False}, {"ready": True, "disk_pressure": True}])
    assert r["not_ready"] == 1
    assert r["pressure"] == 1
    assert not r["all_healthy"]
