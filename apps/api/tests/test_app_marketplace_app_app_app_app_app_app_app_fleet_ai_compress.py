from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_compress import fleet_ai_model_compression
def test_mc():
    r = fleet_ai_model_compression([{"active": True, "models_compressed": 30, "size_reduction_pct": 75, "quality_loss_pct": 0.5}])
    assert r["avg_reduction"] == 75.0
    assert r["efficient"]
