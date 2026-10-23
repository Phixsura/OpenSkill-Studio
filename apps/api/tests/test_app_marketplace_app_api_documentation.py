from app.services.app_marketplace_app_api_documentation import build_api_docs, search_docs

def test_build():
    endpoints = [
        {"method": "GET", "path": "/apps", "summary": "List apps", "tag": "apps"},
        {"method": "POST", "path": "/apps", "summary": "Create app", "tag": "apps", "auth_required": True},
        {"method": "GET", "path": "/users", "summary": "List users", "tag": "users"},
    ]
    r = build_api_docs(title="MyAPI", version="1.0", base_url="https://api.example.com", endpoints=endpoints)
    assert r["total_endpoints"] == 3
    assert r["total_tags"] == 2
    assert r["title"] == "MyAPI"

def test_xss():
    r = build_api_docs(title="<script>alert(1)</script>", version="1.0", base_url="x", endpoints=[])
    assert "<script>" not in r["title"]

def test_search():
    endpoints = [{"path": "/apps", "summary": "List apps"}, {"path": "/users", "summary": "List users"}]
    r = search_docs(query="apps", endpoints=endpoints)
    assert r["total"] == 1
