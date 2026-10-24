from app.services.app_marketplace_app_app_app_marketplace_footer import build_marketplace_footer

def test_footer():
    r = build_marketplace_footer(year=2026)
    assert r["section_count"] == 4
    assert r["total_links"] == 14
    assert "2026" in r["copyright"]
    assert len(r["social"]) == 3
    assert "Marketplace" in r["sections"]
