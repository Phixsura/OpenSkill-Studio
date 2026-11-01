from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_workspace_mgr_v9 import fleet_workspace_mgr_v9
def test_ws_v9():
    r = fleet_workspace_mgr_v9([{"status": "running", "cpu_cores": 8}, {"status": "idle", "cpu_cores": 4}])
    assert r["running"] == 1
    assert r["total_cpu_cores"] == 12
    assert r["healthy"]
