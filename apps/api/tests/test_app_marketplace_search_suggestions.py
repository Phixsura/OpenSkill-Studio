from app.services.app_marketplace_search_suggestions import get_suggestions, track_search, get_popular_searches

def test_suggestions():
    apps = [{"name": "Slack Bot", "id": "a1"}, {"name": "GitHub Sync", "id": "a2"}]
    r = get_suggestions(query="slack", apps=apps, categories=["Connectors"], recent_searches=[])
    assert any(s["text"] == "Slack Bot" for s in r["suggestions"])

def test_category_match():
    r = get_suggestions(query="conn", apps=[], categories=["Connectors", "Analytics"], recent_searches=[])
    assert any(s["type"] == "category" for s in r["suggestions"])

def test_short_query():
    r = get_suggestions(query="s", apps=[], categories=[], recent_searches=["slack integration"])
    assert r["suggestions"] == []

def test_track():
    r = track_search(query="webhook", results_count=5, clicked_result="a1")
    assert r["converted"]

def test_popular():
    logs = [{"query": "webhook"}] * 5 + [{"query": "oauth"}] * 3
    r = get_popular_searches(search_logs=logs)
    assert r[0]["query"] == "webhook"
    assert r[0]["count"] == 5
