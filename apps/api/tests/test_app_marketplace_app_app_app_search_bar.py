from app.services.app_marketplace_app_app_app_search_bar import get_suggestions

def test_suggestions():
    apps = [{"id": "a1", "name": "Code Editor"}, {"id": "a2", "name": "Code Linter"}]
    docs = [{"title": "API Reference", "path": "/docs/api"}]
    r = get_suggestions(query="code", apps=apps, docs=docs)
    assert r["total"] == 2
    assert "Apps" in r["sections"]

def test_short_query():
    r = get_suggestions(query="c", apps=[{"id": "1", "name": "Code"}])
    assert r["total"] == 0

def test_no_match():
    r = get_suggestions(query="zzz", apps=[{"id": "1", "name": "App"}])
    assert r["total"] == 0
