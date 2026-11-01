from app.services.app_marketplace_app_app_app_app_app_app_app_doc_sitemap import get_sitemap, find_doc, get_breadcrumbs

def test_sitemap():
    s = get_sitemap()
    assert len(s) == 3
    assert s[0]["title"] == "Getting Started"

def test_find():
    r = find_doc("authentication")
    assert r is not None
    assert r["title"] == "Authentication"
    assert r["parent"] == "api-reference"

def test_breadcrumbs():
    b = get_breadcrumbs("webhooks")
    assert len(b) == 3
    assert b[0]["title"] == "Docs"
    assert b[1]["title"] == "API Reference"
    assert b[2]["title"] == "Webhooks API"
