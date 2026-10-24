from app.services.app_marketplace_app_app_app_app_app_app_app_ep_catalog import build_catalog, search_endpoints

def test_catalog():
    r = build_catalog([
        {"path": "/api/users", "method": "GET", "tag": "users", "description": "List users"},
        {"path": "/api/users", "method": "POST", "tag": "users", "description": "Create user"},
        {"path": "/api/health", "method": "GET", "tag": "system", "description": "Health check"},
    ])
    assert r["total"] == 3
    assert r["by_tag"]["users"] == 2
    assert r["by_method"]["GET"] == 2

def test_search():
    catalog = build_catalog([
        {"path": "/api/users", "method": "GET", "description": "List users"},
        {"path": "/api/orders", "method": "GET", "description": "List orders"},
    ])
    r = search_endpoints(catalog, "users")
    assert len(r) == 1
    assert r[0]["path"] == "/api/users"
