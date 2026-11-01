from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_hf import fleet_hf_status
def test_hf():
    r = fleet_hf_status([{"running": True, "models": 50, "inferences_24h": 3000000}])
    assert r["models"] == 50
    assert r["all_running"]
