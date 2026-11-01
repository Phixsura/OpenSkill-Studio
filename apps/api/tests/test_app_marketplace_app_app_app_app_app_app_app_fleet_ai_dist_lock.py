from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dist_lock import fleet_ai_distributed_lock
def test_dl():
    r = fleet_ai_distributed_lock([{"active": True, "active_locks": 50, "acquisitions_24h": 500000, "contentions": 10}])
    assert r["locks"] == 50
    assert r["healthy"]
