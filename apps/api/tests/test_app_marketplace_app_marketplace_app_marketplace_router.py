from app.services.app_marketplace_app_marketplace_app_marketplace_router import get_all_routes, get_public_routes, get_protected_routes, match_route, build_sitemap_urls

def test_all():
    r = get_all_routes()
    assert len(r) >= 22

def test_public():
    r = get_public_routes()
    assert all(not x["auth_required"] for x in r)
    assert len(r) >= 10

def test_protected():
    r = get_protected_routes()
    assert all(x["auth_required"] for x in r)

def test_match():
    r = match_route(path="/marketplace")
    assert r["page"] == "home"

def test_match_param():
    r = match_route(path="/marketplace/apps/super-app")
    assert r["page"] == "app_detail"

def test_no_match():
    assert match_route(path="/nonexistent") is None

def test_sitemap():
    urls = build_sitemap_urls()
    assert any("/marketplace" in u for u in urls)
    assert all("/:" not in u for u in urls)
