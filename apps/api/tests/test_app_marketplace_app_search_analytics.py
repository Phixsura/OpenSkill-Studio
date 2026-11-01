from app.services.app_marketplace_app_search_analytics import analyze_search_queries

def test_analytics():
    queries = [
        {"query": "auth sdk", "results_count": 5, "click_count": 2},
        {"query": "auth sdk", "results_count": 5, "click_count": 1},
        {"query": "payment", "results_count": 3, "click_count": 0},
        {"query": "foo bar", "results_count": 0, "click_count": 0},
    ]
    r = analyze_search_queries(queries=queries)
    assert r["total_searches"] == 4
    assert r["unique_queries"] == 3
    assert r["top_queries"][0]["query"] == "auth sdk"
    assert r["top_queries"][0]["count"] == 2
    assert "foo bar" in r["zero_result_queries"]
    assert r["zero_result_rate"] == 25.0

def test_empty():
    r = analyze_search_queries(queries=[])
    assert r["total_searches"] == 0
    assert r["click_through_rate"] == 0
