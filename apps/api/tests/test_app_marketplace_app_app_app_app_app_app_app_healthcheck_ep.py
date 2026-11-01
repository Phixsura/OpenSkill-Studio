from app.services.app_marketplace_app_app_app_app_app_app_app_healthcheck_ep import (
    build_health_response, liveness_probe, readiness_probe,
)

def test_health():
    r = build_health_response({
        "database": {"status": "up", "latency_ms": 5},
        "cache": {"status": "up", "latency_ms": 1},
    })
    assert r["status"] == "pass"
    r2 = build_health_response({"db": {"status": "down", "message": "timeout"}})
    assert r2["status"] == "fail"

def test_liveness():
    assert liveness_probe()["alive"]

def test_readiness():
    r = readiness_probe({"db": True, "cache": True, "queue": False})
    assert not r["ready"]
    assert "queue" in r["not_ready_deps"]
