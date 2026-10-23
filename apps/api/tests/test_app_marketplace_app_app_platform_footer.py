from app.services.app_marketplace_app_app_platform_footer import build_footer

def test_footer():
    r = build_footer(year=2026)
    assert r["brand"]["name"] == "OpenSkill"
    assert len(r["sections"]) == 3
    assert len(r["social"]) == 3
    assert "2026" in r["copyright"]

def test_links():
    r = build_footer()
    product = next(s for s in r["sections"] if s["title"] == "Product")
    assert len(product["links"]) == 4
    assert any(l["label"] == "Marketplace" for l in product["links"])
