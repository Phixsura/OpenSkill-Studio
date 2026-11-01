from app.services.app_marketplace_app_app_app_app_app_app_app_query_profiler import profile_queries

def test_profiler():
    queries = [
        {"query": "SELECT * FROM users WHERE id = 1", "duration_ms": 5, "uses_index": True, "table": "users"},
        {"query": "SELECT * FROM orders", "duration_ms": 1500, "uses_index": False, "scan_type": "full", "table": "orders"},
        {"query": "SELECT * FROM logs WHERE created > now()", "duration_ms": 250, "uses_index": True, "table": "logs"},
    ]
    r = profile_queries(queries)
    assert r["total_queries"] == 3
    assert r["slow_queries"] == 2
    assert r["very_slow"] == 1
    assert r["no_index"] == 1
    assert len(r["suggestions"]) == 2
    assert r["top_slow"][0]["duration_ms"] == 1500
