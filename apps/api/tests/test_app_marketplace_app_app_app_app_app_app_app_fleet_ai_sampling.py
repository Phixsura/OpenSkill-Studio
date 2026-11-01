from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_sampling import fleet_ai_sampling
def test_samp():
    r = fleet_ai_sampling([{"active": True, "rate_pct": 10, "sampled_24h": 10000000, "saved_pct": 90}])
    assert r["rate_pct"] == 10.0
    assert r["efficient"]
