from app.services.app_marketplace_app_app_app_app_app_app_app_db_conn_stats import analyze_connections, pool_recommendations

def test_analyze():
    r = analyze_connections([
        {"name": "primary", "active": 15, "idle": 5, "max_size": 20, "waiting": 0},
        {"name": "replica", "active": 5, "idle": 15, "max_size": 20, "waiting": 2},
    ])
    assert r["active"] == 20
    assert r["utilization_pct"] == 50.0
    assert r["health"] == "healthy"

def test_recommendations():
    stats = {"utilization_pct": 85, "waiting": 5, "active": 5, "idle": 50}
    recs = pool_recommendations(stats)
    assert len(recs) >= 2
