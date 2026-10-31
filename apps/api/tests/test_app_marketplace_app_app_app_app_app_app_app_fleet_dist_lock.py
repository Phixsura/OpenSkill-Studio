from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dist_lock import fleet_dist_lock
def test_lock():
    r = fleet_dist_lock({"active_locks": 5, "contention_events_24h": 50, "deadlocks_24h": 0})
    assert r["healthy"]
    assert r["active_locks"] == 5
