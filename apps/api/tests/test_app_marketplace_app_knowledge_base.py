from app.services.app_marketplace_app_knowledge_base import search_articles, get_article_stats

def test_search():
    articles = [
        {"id": "a1", "title": "Getting Started with Webhooks", "body": "Learn how...", "tags": ["webhooks"]},
        {"id": "a2", "title": "API Authentication", "body": "OAuth flow...", "tags": ["auth", "api"]},
        {"id": "a3", "title": "Billing FAQ", "body": "Common questions...", "tags": ["billing"]},
    ]
    r = search_articles(query="webhook", articles=articles)
    assert r["total"] == 1
    assert r["results"][0]["id"] == "a1"

def test_search_empty():
    r = search_articles(query="", articles=[{"id": "a1", "title": "X"}])
    assert r["total"] == 1

def test_stats():
    articles = [{"category": "guides", "views": 500}, {"category": "guides", "views": 300},
                {"category": "faq", "views": 200}]
    r = get_article_stats(articles=articles)
    assert r["total_articles"] == 3
    assert r["by_category"]["guides"] == 2
    assert r["total_views"] == 1000
