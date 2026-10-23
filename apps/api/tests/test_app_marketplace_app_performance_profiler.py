from app.services.app_marketplace_app_performance_profiler import create_profile, analyze_slow_queries, suggest_optimizations

def test_profile():
    samples = [{"name": "db_query", "duration_ms": 500, "type": "db"},
               {"name": "api_call", "duration_ms": 200, "type": "network"}]
    p = create_profile(app_id="a1", duration_ms=800, samples=samples)
    assert p["bottleneck"]["name"] == "db_query"
    assert len(p["hotspots"]) == 2

def test_slow_queries():
    queries = [{"query": "SELECT *", "duration_ms": 200}, {"query": "INSERT", "duration_ms": 50}]
    r = analyze_slow_queries(queries=queries, threshold_ms=100)
    assert r["slow_count"] == 1

def test_suggestions_slow():
    s = suggest_optimizations(profile={"total_ms": 2000, "bottleneck": {"type": "db"}})
    assert any("async" in x for x in s)
    assert any("indexes" in x for x in s)

def test_suggestions_ok():
    s = suggest_optimizations(profile={"total_ms": 100, "bottleneck": None})
    assert "good" in s[0]
