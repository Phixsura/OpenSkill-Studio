from app.services.app_marketplace_sitemap import generate_sitemap

APPS = [{"slug": "my-app", "developer_slug": "dev-co", "updated_at": "2026-01-01"},
        {"slug": "other-app", "developer_slug": "dev-co"}]

def test_contains_xml():
    sm = generate_sitemap(APPS)
    assert '<?xml' in sm
    assert '<urlset' in sm

def test_contains_app_urls():
    sm = generate_sitemap(APPS)
    assert "my-app" in sm
    assert "other-app" in sm

def test_contains_developer():
    sm = generate_sitemap(APPS)
    assert "dev-co" in sm

def test_static_pages():
    sm = generate_sitemap([])
    assert "/apps" in sm
    assert "/categories" in sm
