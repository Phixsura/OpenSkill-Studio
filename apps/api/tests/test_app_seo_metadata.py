from app.services.app_seo_metadata import build_app_seo, build_category_seo

def test_app_seo():
    s = build_app_seo({"name": "My App", "slug": "my-app", "description": "Great app"})
    assert "My App" in s["title"]
    assert "my-app" in s["canonical"]
    assert s["og"]["type"] == "website"

def test_category_seo():
    s = build_category_seo("connector")
    assert "Connectors" in s["title"]

def test_truncate_desc():
    s = build_app_seo({"name": "X", "slug": "x", "description": "a" * 300})
    assert len(s["description"]) <= 160
