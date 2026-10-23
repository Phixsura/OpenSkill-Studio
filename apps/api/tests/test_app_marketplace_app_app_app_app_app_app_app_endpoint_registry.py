from app.services.app_marketplace_app_app_app_app_app_app_app_endpoint_registry import list_endpoints, search_endpoints, get_categories

def test_list():
    all_eps = list_endpoints()
    assert len(all_eps) == 10
    apps_eps = list_endpoints(category="apps")
    assert len(apps_eps) == 5
    auth_eps = list_endpoints(auth_only=True)
    assert all(e["auth"] for e in auth_eps)

def test_search():
    r = search_endpoints("webhook")
    assert len(r) == 2

def test_categories():
    cats = get_categories()
    assert any(c["category"] == "apps" for c in cats)
