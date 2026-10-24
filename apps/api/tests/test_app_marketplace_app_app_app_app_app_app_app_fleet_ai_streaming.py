from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_streaming import fleet_ai_streaming
def test_st():
    r = fleet_ai_streaming([{"active": True, "connections": 50000, "tokens_per_sec": 100000, "ttft_ms": 120}])
    assert r["tokens_per_sec"] == 100000
    assert r["responsive"]
