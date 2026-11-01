from app.services.app_marketplace_app_app_footer_links import build_footer

def test_default():
    r = build_footer()
    assert r["section_count"] == 4
    assert r["total_links"] == 15
    assert "2026" in r["copyright"]
    assert "Product" in r["sections"]

def test_custom():
    r = build_footer(sections={"Help": [{"label": "FAQ", "href": "/faq"}]}, company="Acme")
    assert r["section_count"] == 1
    assert "Acme" in r["copyright"]
