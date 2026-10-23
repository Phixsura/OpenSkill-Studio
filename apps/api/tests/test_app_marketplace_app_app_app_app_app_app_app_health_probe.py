from app.services.app_marketplace_app_app_app_app_app_app_app_health_probe import liveness_check, readiness_check, startup_check

def test_liveness():
    r = liveness_check()
    assert r["status"] == "alive"

def test_readiness():
    r = readiness_check([
        {"name": "database", "healthy": True, "latency_ms": 5},
        {"name": "cache", "healthy": False, "latency_ms": 0},
    ])
    assert not r["ready"]
    assert r["status"] == "not_ready"

def test_startup():
    r = startup_check(required_env=["DB_URL", "API_KEY"],
                        actual_env={"DB_URL": "postgres://...", "API_KEY": "sk_..."})
    assert r["ready"]
    r2 = startup_check(required_env=["DB_URL", "MISSING"], actual_env={"DB_URL": "x"})
    assert not r2["ready"]
    assert "MISSING" in r2["missing_env"]
