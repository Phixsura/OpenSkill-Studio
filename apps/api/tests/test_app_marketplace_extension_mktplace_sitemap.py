from app.services.app_marketplace_extension_mktplace_sitemap import MktplaceSitemapService

def test_generate():
    svc = MktplaceSitemapService()
    svc.add("/", 1.0, "daily")
    svc.add_extensions(["ext-1", "ext-2"])
    xml = svc.generate_xml()
    assert '<?xml version="1.0"' in xml
    assert "/ext/ext-1" in xml
    assert svc.count() == 3

def test_categories():
    svc = MktplaceSitemapService()
    svc.add_categories(["tools", "analytics"])
    xml = svc.generate_xml()
    assert "/category/tools" in xml
