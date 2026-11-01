from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_threads import fleet_thread_pool
def test_threads():
    r = fleet_thread_pool([{"active_threads": 180, "max_threads": 200}, {"active_threads": 190, "max_threads": 200}])
    assert r["active"] == 370
    assert r["pct"] == 92.5
    assert r["exhausted"]
