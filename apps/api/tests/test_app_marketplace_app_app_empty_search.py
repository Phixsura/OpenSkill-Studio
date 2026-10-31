from app.services.app_marketplace_app_app_empty_search import build_empty_search

def test_empty():
    r = build_empty_search(query="xyznonexistent")
    assert "xyznonexistent" in r["title"]
    assert len(r["suggestions"]) == 4
    assert len(r["popular_searches"]) == 5
    assert r["icon"] == "🔍"

def test_custom_suggestions():
    r = build_empty_search(query="test", suggestions=["Try again"])
    assert r["suggestions"] == ["Try again"]
