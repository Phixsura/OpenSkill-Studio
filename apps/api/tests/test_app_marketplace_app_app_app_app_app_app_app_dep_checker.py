from app.services.app_marketplace_app_app_app_app_app_app_app_dep_checker import check_dependencies, suggest_fallbacks

def test_check():
    r = check_dependencies([
        {"name": "postgres", "type": "database", "status": "healthy", "latency_ms": 5},
        {"name": "redis", "type": "cache", "status": "healthy", "latency_ms": 2},
        {"name": "email-api", "type": "service", "status": "unhealthy", "latency_ms": 0},
    ])
    assert r["healthy"] == 2
    assert r["unhealthy"] == 1
    assert "email-api" in r["critical_failures"]

def test_fallbacks():
    fb = suggest_fallbacks(["redis", "email"], {"redis": "in-memory"})
    assert fb[0]["has_fallback"]
    assert not fb[1]["has_fallback"]
