from app.services.app_marketplace_app_developer_knowledge_base import search_knowledge_base, get_articles_by_category, get_popular_articles

def test_search():
    r = search_knowledge_base(query="oauth")
    assert r[0]["id"] == "kb-002"

def test_search_tag():
    r = search_knowledge_base(query="webhook")
    assert any(a["id"] == "kb-003" for a in r)

def test_category():
    r = get_articles_by_category(category="auth")
    assert len(r) == 1

def test_popular():
    views = {"kb-005": 1000, "kb-001": 500, "kb-003": 800}
    r = get_popular_articles(view_counts=views, limit=2)
    assert r[0]["id"] == "kb-005"
