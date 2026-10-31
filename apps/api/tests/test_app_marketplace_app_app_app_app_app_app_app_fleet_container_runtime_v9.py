from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_container_runtime_v9 import fleet_container_runtime_v9
def test_crt_v9():
    r = fleet_container_runtime_v9([{"status": "running", "privileged": False, "cpu_millicores": 500}])
    assert r["running"] == 1
    assert r["privileged"] == 0
    assert r["healthy"]
