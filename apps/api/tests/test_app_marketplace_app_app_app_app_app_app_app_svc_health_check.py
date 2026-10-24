from app.services.app_marketplace_app_app_app_app_app_app_app_svc_health_check import run_health_checks

def test_checks():
    r = run_health_checks([
        {"name": "api", "checks": {"db": True, "cache": True}, "latency_ms": 5},
        {"name": "worker", "checks": {"db": True, "queue": False}, "latency_ms": 10},
    ])
    assert r["healthy"] == 1
    assert r["overall"] == "degraded"
    assert r["health_pct"] == 50
