from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_arch import fleet_ai_model_archive
def test_ma():
    r = fleet_ai_model_archive([{"active": True, "models": 5000, "storage_tb": 2000, "retrievals": 100}])
    assert r["models"] == 5000
    assert r["preserved"]
