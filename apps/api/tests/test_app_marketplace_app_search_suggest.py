from app.services.app_marketplace_app_search_suggest import get_suggestions, get_trending_searches

def test_suggest():
    catalog = [
        {"id": "a1", "name": "Auth SDK", "category": "security"},
        {"id": "a2", "name": "Analytics Pro", "category": "analytics"},
        {"id": "a3", "name": "Basic Auth", "category": "security"},
    ]
    r = get_suggestions(query="auth", catalog=catalog)
    assert r["total"] == 2  # Auth SDK (starts with) + Basic Auth (contains)
    assert r["suggestions"][0]["text"] == "Auth SDK"

def test_too_short():
    r = get_suggestions(query="a", catalog=[])
    assert len(r["suggestions"]) == 0

def test_trending():
    queries = ["auth", "payment", "auth", "auth", "analytics", "payment"]
    r = get_trending_searches(recent_queries=queries)
    assert r["trending"][0]["query"] == "auth"
    assert r["trending"][0]["count"] == 3
