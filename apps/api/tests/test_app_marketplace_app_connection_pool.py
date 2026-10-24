from app.services.app_marketplace_app_connection_pool import get_pool_status, recommend_pool_size

def test_healthy():
    pools = [{"name": "primary", "active": 5, "idle": 10, "max_size": 20, "waiting": 0}]
    r = get_pool_status(pools=pools)
    assert r["overall_health"] == "healthy"
    assert r["pools"][0]["utilization_pct"] == 25.0

def test_exhausted():
    pools = [{"name": "primary", "active": 19, "idle": 1, "max_size": 20, "waiting": 5}]
    r = get_pool_status(pools=pools)
    assert r["overall_health"] == "critical"

def test_recommend():
    r = recommend_pool_size(avg_queries_per_sec=50, avg_query_ms=20)
    assert r["recommended_pool_size"] >= 5
    assert r["avg_concurrent_queries"] == 1.0
