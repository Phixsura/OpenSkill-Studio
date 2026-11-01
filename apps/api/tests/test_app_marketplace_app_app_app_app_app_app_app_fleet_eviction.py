from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_eviction import fleet_eviction_tracker
def test_eviction():
    r = fleet_eviction_tracker([{"reason": "node_pressure"}, {"reason": "preempted"}, {"reason": "node_pressure"}])
    assert r["total"] == 3
    assert r["by_reason"]["node_pressure"] == 2
