from app.services.app_marketplace_app_sitemap_generator import generate_sitemap

def test_generate():
    pages = [
        {"path": "/", "lastmod": "2026-10-23", "priority": 1.0},
        {"path": "/apps", "lastmod": "2026-10-22", "priority": 0.8},
    ]
    r = generate_sitemap(base_url="https://marketplace.openskill.dev", pages=pages)
    assert r["url_count"] == 2
    assert "<urlset" in r["xml"]
    assert "marketplace.openskill.dev/" in r["xml"]

def test_escaping():
    pages = [{"path": "/search?q=foo&bar=1"}]
    r = generate_sitemap(base_url="https://x.com", pages=pages)
    assert "&amp;" in r["xml"]
