from app.services.app_marketplace_app_app_app_app_app_app_app_query_analyzer import analyze_query, top_slow_queries

def test_analyze():
    r = analyze_query("SELECT * FROM users WHERE id = 1", 5.0, 1, 1, True)
    assert r["efficiency_pct"] == 100.0
    assert not r["slow"]
    assert len(r["suggestions"]) == 0

def test_slow():
    r = analyze_query("SELECT * FROM logs", 500.0, 100000, 100000, False)
    assert r["slow"]
    assert len(r["suggestions"]) >= 2

def test_top():
    queries = [{"execution_ms": 10}, {"execution_ms": 500}, {"execution_ms": 50}]
    top = top_slow_queries(queries, 2)
    assert top[0]["execution_ms"] == 500
    assert len(top) == 2
