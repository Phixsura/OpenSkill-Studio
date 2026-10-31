from app.services.app_marketplace_app_app_app_app_app_app_app_search_suggest import get_suggestions, get_trending_searches, build_search_page

def test_suggestions():
    r = get_suggestions("sl")
    assert len(r) == 1
    assert "slack" in r[0]

def test_empty():
    r = get_suggestions("")
    assert len(r) == 5  # returns popular

def test_trending():
    assert len(get_trending_searches()) == 6

def test_page():
    r = build_search_page("api")
    assert r["suggestion_count"] >= 1
    assert not r["show_trending"]
