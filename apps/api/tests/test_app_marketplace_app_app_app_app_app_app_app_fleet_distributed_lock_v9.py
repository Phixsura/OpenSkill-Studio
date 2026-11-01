from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_distributed_lock_v9 import fleet_distributed_lock_v9
def test_dl2_v9():
    r = fleet_distributed_lock_v9([{"held": True, "contention_count": 0, "hold_ms": 50}])
    assert r["contended"] == 0
    assert r["healthy"]
