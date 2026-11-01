from app.services.app_marketplace_extension_sitemap import MarketplaceSitemapService


def test_add_extensions():
    svc = MarketplaceSitemapService()
    count = svc.add_extensions([{"id": "ext-1"}, {"id": "ext-2"}])
    assert count == 2


def test_generate_xml():
    svc = MarketplaceSitemapService()
    svc.add_extensions([{"id": "ext-1", "updated": "2024-06-01"}])
    svc.add_categories(["tools", "analytics"])
    xml = svc.generate_xml()
    assert '<?xml version="1.0"' in xml
    assert "ext-1" in xml
    assert "tools" in xml
    assert "<priority>1.0</priority>" in xml  # homepage


def test_stats():
    svc = MarketplaceSitemapService()
    svc.add_extensions([{"id": "e1"}, {"id": "e2"}])
    svc.add_categories(["tools"])
    svc.add_developers([{"id": "d1"}])
    svc.add_docs([{"slug": "quickstart"}])
    stats = svc.get_stats()
    assert stats["total_urls"] == 6  # 2+1+1+1 + homepage
    assert stats["extensions"] == 2


def test_lastmod():
    svc = MarketplaceSitemapService()
    svc.add_extensions([{"id": "e1", "updated": "2024-10-27"}])
    xml = svc.generate_xml()
    assert "2024-10-27" in xml
