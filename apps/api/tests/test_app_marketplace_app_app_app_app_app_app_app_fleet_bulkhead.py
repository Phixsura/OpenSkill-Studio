from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_bulkhead import fleet_bulkhead
def test_bh():
    r = fleet_bulkhead([{"active_threads": 8, "max_threads": 10, "rejected": 0}, {"active_threads": 10, "max_threads": 10, "rejected": 5}])
    assert r["active"] == 18
    assert r["rejected"] == 5
    assert not r["healthy"]
