from app.services.app_marketplace_app_app_app_marketplace_search_bar import build_search_suggestions

def test_no_query():
    r = build_search_suggestions(query="", recent_searches=["webhook", "deploy"])
    assert r["show_popular"]
    assert len(r["recent_searches"]) == 2

def test_with_query():
    r = build_search_suggestions(query="code")
    assert r["show_matched"]
    assert "code editor" in r["matched_popular"]

def test_no_match():
    r = build_search_suggestions(query="zzzzz")
    assert not r["show_matched"]
