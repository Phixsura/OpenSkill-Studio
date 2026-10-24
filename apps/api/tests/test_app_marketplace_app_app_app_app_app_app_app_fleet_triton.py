from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_triton import fleet_triton_status
def test_triton():
    r = fleet_triton_status([{"ready": True, "models_loaded": 10, "inferences_per_sec": 50000}])
    assert r["models_loaded"] == 10
    assert r["all_ready"]
