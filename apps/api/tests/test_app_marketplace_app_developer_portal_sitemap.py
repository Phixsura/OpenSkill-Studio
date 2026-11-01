from app.services.app_marketplace_app_developer_portal_sitemap import get_portal_navigation, get_breadcrumb

def test_nav():
    n = get_portal_navigation()
    assert len(n) == 10
    assert n[0]["path"] == "/developer"

def test_breadcrumb():
    b = get_breadcrumb(path="/developer/analytics")
    assert len(b) == 2
    assert b[1]["title"] == "Analytics"

def test_breadcrumb_root():
    b = get_breadcrumb(path="/developer")
    assert len(b) == 1
