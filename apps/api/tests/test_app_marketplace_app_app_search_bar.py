from app.services.app_marketplace_app_app_search_bar import build_search_bar_config, filter_search_history

def test_config():
    r = build_search_bar_config(placeholder="Search apps...", shortcut="Ctrl+K")
    assert r["placeholder"] == "Search apps..."
    assert r["debounce_ms"] == 300
    assert r["min_query_length"] == 2

def test_history():
    history = ["auth sdk", "payment gateway", "chart library", "auth helper"]
    r = filter_search_history(history=history, current_query="auth", limit=3)
    assert len(r["suggestions"]) == 2
    assert r["from_history"]

def test_empty_query():
    r = filter_search_history(history=["a", "b", "c"], current_query="", limit=2)
    assert len(r["suggestions"]) == 2
