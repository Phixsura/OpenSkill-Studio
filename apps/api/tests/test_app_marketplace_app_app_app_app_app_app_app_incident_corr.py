from app.services.app_marketplace_app_app_app_app_app_app_app_incident_corr import correlate_incidents

def test_correlated():
    r = correlate_incidents([
        {"service": "api", "timestamp": 1000, "title": "High errors"},
        {"service": "db", "timestamp": 1010, "title": "Connection pool exhausted"},
        {"service": "cache", "timestamp": 1020, "title": "Timeout"},
        {"service": "worker", "timestamp": 5000, "title": "Unrelated"},
    ], window_seconds=60)
    assert r["correlated_groups"] == 1
    assert r["groups"][0]["count"] == 3
    assert r["uncorrelated"] == 1

def test_no_correlation():
    r = correlate_incidents([
        {"service": "api", "timestamp": 1000},
        {"service": "db", "timestamp": 5000},
    ], window_seconds=60)
    assert r["correlated_groups"] == 0
