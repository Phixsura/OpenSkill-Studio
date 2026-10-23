from app.services.app_marketplace_app_app_app_app_app_app_app_load_balancer import check_backends, recommend_scaling

def test_backends():
    backends = [
        {"id": "i-1", "healthy": True, "rps": 500, "latency_ms": 45, "weight": 1},
        {"id": "i-2", "healthy": True, "rps": 480, "latency_ms": 50, "weight": 1},
        {"id": "i-3", "healthy": False, "rps": 0, "latency_ms": 0, "weight": 1},
    ]
    r = check_backends(backends)
    assert r["healthy"] == 2
    assert r["unhealthy"] == 1
    assert r["status"] == "degraded"
    assert r["total_rps"] == 980

def test_scaling():
    backends = [
        {"id": "i-1", "healthy": True, "rps": 900},
        {"id": "i-2", "healthy": True, "rps": 950},
    ]
    r = recommend_scaling(backends, target_rps_per_instance=1000)
    assert r["recommended"] == 2
    assert r["action"] == "none"
    r2 = recommend_scaling(backends + [{"id": "i-3", "healthy": True, "rps": 800}], target_rps_per_instance=1000)
    assert r2["recommended"] == 3
    assert r2["action"] == "none"
