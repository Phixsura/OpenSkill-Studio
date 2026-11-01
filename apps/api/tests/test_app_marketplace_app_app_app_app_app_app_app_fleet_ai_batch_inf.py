from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_batch_inf import fleet_ai_batch_inference
def test_bi():
    r = fleet_ai_batch_inference([{"status": "completed", "samples": 10000000, "latency_ms": 12}])
    assert r["completed"] == 1
    assert r["total_samples"] == 10000000
