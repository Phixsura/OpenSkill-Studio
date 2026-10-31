from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ml_serving import fleet_ml_serving
def test_ml():
    r = fleet_ml_serving([{"qps": 1000, "p99_ms": 50, "model_age_days": 10}, {"qps": 500, "p99_ms": 30, "model_age_days": 100}])
    assert r["total_qps"] == 1500
    assert r["stale_models"] == 1
    assert r["performant"]
