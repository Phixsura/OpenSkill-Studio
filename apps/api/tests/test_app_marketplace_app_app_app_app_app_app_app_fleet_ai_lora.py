from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_lora import fleet_ai_lora
def test_lora():
    r = fleet_ai_lora([{"active": True, "rank": 64, "trained": 200, "param_pct": 0.1}])
    assert r["rank"] == 64
    assert r["efficient"]
