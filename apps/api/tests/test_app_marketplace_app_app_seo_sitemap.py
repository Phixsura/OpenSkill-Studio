from app.services.app_marketplace_app_app_seo_sitemap import generate_marketplace_sitemap

def test_sitemap():
    apps = [{"id": "auth", "updated_at": "2026-10-23"}, {"id": "charts"}]
    categories = [{"id": "tools"}, {"id": "design"}]
    developers = [{"id": "alice"}]
    r = generate_marketplace_sitemap(base_url="https://marketplace.dev",
        apps=apps, categories=categories, developers=developers)
    assert r["static_pages"] == 6
    assert r["dynamic_pages"] == 5  # 2 apps + 2 cats + 1 dev
    assert r["total_urls"] == 11

def test_empty():
    r = generate_marketplace_sitemap(base_url="https://x.com", apps=[], categories=[], developers=[])
    assert r["total_urls"] == 6  # only static
