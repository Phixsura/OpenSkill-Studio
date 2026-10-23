from app.services.app_marketplace_app_app_app_app_app_app_app_global_search import search

def test_search():
    sources = [
        {"title": "User Management", "description": "Manage users and roles", "type": "page", "url": "/users"},
        {"title": "API Keys", "description": "Manage API keys", "type": "settings", "url": "/settings/keys"},
        {"title": "Billing", "description": "Payment and invoices", "type": "page", "url": "/billing"},
    ]
    r = search("manage", sources=sources)
    assert r["total"] == 2
    assert r["results"][0]["title"] in ("User Management", "API Keys")
    r2 = search("billing", sources=sources)
    assert r2["total"] == 1
    assert r2["results"][0]["url"] == "/billing"

def test_empty():
    r = search("", sources=[{"title": "Test"}])
    assert r["total"] == 0
