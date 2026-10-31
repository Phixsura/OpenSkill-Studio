from app.services.app_marketplace_app_app_app_app_app_app_app_knowledge_base import (
    create_article, search_articles, rate_article, kb_stats, clear_kb,
)

def test_search():
    clear_kb()
    create_article("getting-started", "Getting Started", "How to begin", "guides", ["setup"])
    create_article("api-auth", "API Authentication", "Auth guide", "api", ["auth"])
    r = search_articles("auth")
    assert len(r) == 1
    assert r[0]["slug"] == "api-auth"
    r2 = search_articles("guide")
    assert len(r2) == 1  # only content match in api-auth
    clear_kb()

def test_rate():
    clear_kb()
    create_article("test", "Test", "Content", "misc")
    rate_article("test", True)
    rate_article("test", True)
    r = rate_article("test", False)
    assert r["helpful_pct"] == 67
    clear_kb()
