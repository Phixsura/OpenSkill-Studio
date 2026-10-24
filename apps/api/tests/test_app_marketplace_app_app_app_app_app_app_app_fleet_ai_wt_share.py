from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_wt_share import fleet_ai_weight_sharing
def test_ws():
    r = fleet_ai_weight_sharing([{"active": True, "shared_layers": 48, "saved_gb": 200, "models": 10}])
    assert r["shared_layers"] == 48
    assert r["efficient"]
