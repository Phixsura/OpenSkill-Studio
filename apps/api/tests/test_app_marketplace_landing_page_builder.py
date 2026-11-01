from app.services.app_marketplace_landing_page_builder import build_app_landing_page, get_section_templates

def test_page():
    sections = [{"type": "hero", "content": {"title": "Welcome"}, "order": 0},
                {"type": "features", "content": {"items": []}, "order": 1}]
    p = build_app_landing_page(app={"name": "MyApp", "slug": "my-app"}, sections=sections)
    assert p["section_count"] == 2
    assert p["sections"][0]["type"] == "hero"
    assert "MyApp" in p["seo"]["title"]

def test_templates():
    t = get_section_templates()
    assert len(t) >= 6
    assert "hero" in t
    assert "pricing" in t
