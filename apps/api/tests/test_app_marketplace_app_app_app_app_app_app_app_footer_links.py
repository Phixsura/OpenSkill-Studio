from app.services.app_marketplace_app_app_app_app_app_app_app_footer_links import build_footer

def test_footer():
    r = build_footer()
    assert r["section_count"] == 4
    assert r["total_links"] == 16
    assert r["copyright"] == "© 2026 OpenSkill"
    assert r["sections"][0]["title"] == "Product"

def test_custom():
    r = build_footer(sections=[
        {"title": "Links", "links": [{"label": "Home", "url": "/"}]}
    ])
    assert r["section_count"] == 1
    assert r["total_links"] == 1
