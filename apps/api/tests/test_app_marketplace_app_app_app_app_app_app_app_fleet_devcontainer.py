from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_devcontainer import fleet_devcontainer_status
def test_dc():
    r = fleet_devcontainer_status([{"status": "running", "startup_sec": 30}, {"status": "running", "startup_sec": 45}])
    assert r["running"] == 2
    assert r["avg_startup_sec"] == 37.5
    assert r["fast"]
