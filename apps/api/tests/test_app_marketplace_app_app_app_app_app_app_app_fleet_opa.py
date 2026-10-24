from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_opa import fleet_opa_decisions
def test_opa():
    r = fleet_opa_decisions([{"evaluations": 10000, "denied": 500, "latency_ms": 2}, {"evaluations": 5000, "denied": 100, "latency_ms": 3}])
    assert r["total_evaluations"] == 15000
    assert r["denied"] == 600
    assert r["avg_latency_ms"] == 2.5
