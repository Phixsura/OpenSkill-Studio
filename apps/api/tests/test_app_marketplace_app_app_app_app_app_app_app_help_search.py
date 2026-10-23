from app.services.app_marketplace_app_app_app_app_app_app_app_help_search import search_help, get_popular_articles

def test_search():
    articles = [
        {"title": "Getting Started with Webhooks", "body": "Learn how to set up webhooks", "tags": ["webhooks"], "url": "/help/webhooks"},
        {"title": "API Authentication", "body": "How to authenticate API requests", "tags": ["auth", "api"], "url": "/help/auth"},
        {"title": "Billing FAQ", "body": "Common billing questions", "tags": ["billing"], "url": "/help/billing"},
    ]
    r = search_help("webhook", articles)
    assert r["total"] == 1
    assert r["results"][0]["title"] == "Getting Started with Webhooks"
    r2 = search_help("api", articles)
    assert r2["total"] == 1

def test_popular():
    articles = [{"title": "A", "views": 100}, {"title": "B", "views": 500}, {"title": "C", "views": 200}]
    r = get_popular_articles(articles, limit=2)
    assert r[0]["title"] == "B"
    assert len(r) == 2
