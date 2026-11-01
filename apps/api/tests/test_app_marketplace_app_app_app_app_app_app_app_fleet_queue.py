from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_queue import fleet_queue_depth
def test_queue():
    r = fleet_queue_depth([{"depth": 5000}, {"depth": 3000}, {"depth": 4000}])
    assert r["total_depth"] == 12000
    assert r["max_depth"] == 5000
    assert r["backlog"]
