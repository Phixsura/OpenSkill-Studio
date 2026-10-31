from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_grad_ckpt import fleet_ai_gradient_checkpoint
def test_gc():
    r = fleet_ai_gradient_checkpoint([{"active": True, "saved_gb": 500, "overhead_pct": 15, "jobs": 50}])
    assert r["saved_gb"] == 500
    assert r["efficient"]
