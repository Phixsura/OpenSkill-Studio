from app.services.app_marketplace_search_analytics import record_search, get_top_searches, get_zero_result_queries

def test_record():
    record_search(query="lms connector", results_count=5)
    top = get_top_searches(limit=10)
    assert any(t["term"] == "lms" for t in top)

def test_zero_results():
    record_search(query="nonexistent thing", results_count=0)
    record_search(query="nonexistent thing", results_count=0)
    zeros = get_zero_result_queries()
    assert "nonexistent thing" in zeros

def test_top_sorted():
    for _ in range(10):
        record_search(query="popular search", results_count=3)
    top = get_top_searches(limit=5)
    assert top[0]["count"] >= 10
