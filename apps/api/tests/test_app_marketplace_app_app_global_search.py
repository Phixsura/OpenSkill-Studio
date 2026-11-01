from app.services.app_marketplace_app_app_global_search import global_search

def test_search():
    apps = [{"id": "a1", "name": "Code Editor", "description": "Edit code"}]
    docs = [{"title": "API Reference", "path": "/docs/api"}]
    r = global_search(query="code", apps=apps, docs=docs)
    assert r["total"] >= 1
    assert "Apps" in r["sections"]

def test_empty():
    r = global_search(query="")
    assert r["total"] == 0

def test_no_match():
    r = global_search(query="zzz", apps=[{"id": "1", "name": "X", "description": "Y"}])
    assert r["total"] == 0
