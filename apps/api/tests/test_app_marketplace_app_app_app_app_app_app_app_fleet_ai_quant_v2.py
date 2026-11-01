from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_quant_v2 import fleet_ai_quantizer_v2
def test_qv2():
    r = fleet_ai_quantizer_v2([{"active": True, "models": 100, "bits": 4, "speedup_x": 4, "loss_pct": 0.5}])
    assert r["bits"] == 4
    assert r["efficient"]
