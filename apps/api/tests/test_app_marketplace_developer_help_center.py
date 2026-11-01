from app.services.app_marketplace_developer_help_center import build_help_center, search_help

def test_center():
    c = build_help_center()
    assert len(c["sections"]) == 7
    assert c["total_articles"] > 50
    assert c["search_enabled"]

def test_search():
    articles = [{"title": "OAuth Guide", "content": "How to implement OAuth", "tags": ["auth"]},
                {"title": "Webhook Setup", "content": "Configure webhooks", "tags": ["webhook"]}]
    r = search_help(query="oauth", articles=articles)
    assert len(r) == 1
    assert r[0]["title"] == "OAuth Guide"
