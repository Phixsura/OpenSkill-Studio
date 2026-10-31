from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_node_sched import fleet_ai_node_scheduler
def test_ns():
    r = fleet_ai_node_scheduler([{"active": True, "nodes": 1000, "placements_24h": 50000, "preemptions": 5}])
    assert r["nodes"] == 1000
    assert r["optimal"]
