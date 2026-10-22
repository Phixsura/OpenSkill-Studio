from app.services.app_installation_health import aggregate_installation_health

def test_all_healthy():
    r = aggregate_installation_health([{"health_score": 95}, {"health_score": 100}])
    assert r["overall"] == "healthy"
    assert r["healthy"] == 2

def test_critical():
    r = aggregate_installation_health([{"health_score": 30}])
    assert r["overall"] == "critical"

def test_empty():
    r = aggregate_installation_health([])
    assert r["overall"] == "unknown"

def test_mixed():
    r = aggregate_installation_health([{"health_score": 95}, {"health_score": 60}, {"health_score": 40}])
    assert r["critical"] == 1
    assert r["overall"] == "critical"
