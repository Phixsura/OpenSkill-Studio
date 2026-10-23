from app.services.app_marketplace_app_app_help_article import create_help_article, search_help

def test_create():
    r = create_help_article(title="Getting Started with Webhooks", body="Learn how to " * 50,
        category="guides", tags=["webhooks", "api"], author="Alice")
    assert r["slug"] == "getting-started-with-webhooks"
    assert r["read_time_min"] >= 1
    assert r["url"] == "/help/guides/getting-started-with-webhooks"

def test_xss():
    r = create_help_article(title="<script>", body="x", category="x", tags=[], author="x")
    assert "<script>" not in r["title"]

def test_search():
    articles = [
        {"title": "Webhook Guide", "body": "How to use webhooks", "tags": ["webhooks"]},
        {"title": "API Auth", "body": "Authentication guide", "tags": ["auth"]},
    ]
    r = search_help(query="webhook", articles=articles)
    assert r["total"] == 1
    assert r["results"][0]["title"] == "Webhook Guide"
