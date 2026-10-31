from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_skaffold import fleet_skaffold_status
def test_sk():
    r = fleet_skaffold_status([{"dev_loop_active": True, "sync_ms": 2000}, {"dev_loop_active": True, "sync_ms": 3000}])
    assert r["active_loops"] == 2
    assert r["avg_sync_ms"] == 2500.0
    assert r["fast"]
