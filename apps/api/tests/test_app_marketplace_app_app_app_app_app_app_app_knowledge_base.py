from app.services.app_marketplace_app_app_app_app_app_app_app_knowledge_base import KnowledgeBase

def test_kb():
    kb = KnowledgeBase()
    kb.add_article(slug="auth-guide", title="Authentication Guide", body="How to authenticate...",
                    category="guides", tags=["auth", "api"])
    kb.add_article(slug="webhooks-faq", title="Webhooks FAQ", body="Common webhook questions",
                    category="faq", tags=["webhooks"])
    results = kb.search("auth")
    assert len(results) == 1
    assert results[0]["slug"] == "auth-guide"
    v = kb.view("auth-guide")
    assert v["views"] == 1
    r = kb.rate("auth-guide", helpful=True)
    assert r["helpful_pct"] == 100
    s = kb.stats()
    assert s["total_articles"] == 2
