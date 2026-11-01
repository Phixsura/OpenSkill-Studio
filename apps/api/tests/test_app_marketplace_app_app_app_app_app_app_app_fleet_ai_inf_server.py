from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_inf_server import fleet_ai_inference_server
def test_is():
    r = fleet_ai_inference_server([{"healthy": True, "rps": 100000, "ttft_ms": 80, "tokens_per_sec": 500}])
    assert r["rps"] == 100000
    assert r["performant"]
