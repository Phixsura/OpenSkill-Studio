from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_modal import fleet_modal_status
def test_modal():
    r = fleet_modal_status([{"running": True, "gpu_hours_24h": 200, "functions": 50}])
    assert r["gpu_hours_24h"] == 200
    assert r["all_running"]
