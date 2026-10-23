from app.services.app_marketplace_app_app_sitemap_generator import generate_sitemap

def test_sitemap():
    pages = [
        {"path": "/", "priority": 1.0, "changefreq": "daily"},
        {"path": "/apps", "priority": 0.8},
        {"path": "/docs", "priority": 0.6},
    ]
    r = generate_sitemap(base_url="https://marketplace.openskill.dev", pages=pages)
    assert r["url_count"] == 3
    assert "<urlset" in r["xml"]
    assert "marketplace.openskill.dev/apps" in r["xml"]

def test_bad_url():
    r = generate_sitemap(base_url="ftp://bad", pages=[])
    assert "error" in r
