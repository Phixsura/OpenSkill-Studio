from app.services.app_marketplace_search_history import add_to_history, clear_history, get_recent_searches, get_search_analytics

def test_add():
    h = add_to_history(history=["old"], query="new")
    assert h[0] == "new"
    assert h[1] == "old"

def test_dedup():
    h = add_to_history(history=["webhook", "oauth"], query="webhook")
    assert h.count("webhook") == 1
    assert h[0] == "webhook"

def test_max():
    h = add_to_history(history=[f"q{i}" for i in range(25)], query="new", max_items=10)
    assert len(h) == 10

def test_clear():
    assert clear_history() == []

def test_recent():
    h = get_recent_searches(history=["a", "b", "c", "d", "e", "f"], limit=3)
    assert h == ["a", "b", "c"]

def test_analytics():
    searches = [{"query": "webhook", "results_count": 5}, {"query": "oauth", "results_count": 0},
                {"query": "webhook", "results_count": 3}]
    a = get_search_analytics(searches=searches)
    assert a["total"] == 3
    assert a["unique"] == 2
    assert a["zero_results_pct"] > 30
