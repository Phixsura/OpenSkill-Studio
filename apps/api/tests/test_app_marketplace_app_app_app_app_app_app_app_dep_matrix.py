from app.services.app_marketplace_app_app_app_app_app_app_app_dep_matrix import build_matrix

def test_matrix():
    r = build_matrix(["api", "db", "cache"], [
        {"source": "api", "destination": "db", "status": "healthy"},
        {"source": "api", "destination": "cache", "status": "healthy"},
        {"source": "db", "destination": "cache", "status": "degraded"},
    ])
    assert r["healthy_pairs"] == 2
    assert r["total_pairs"] == 3
    assert r["health_pct"] == 66.7
    assert r["matrix"]["api"]["db"] == "healthy"
