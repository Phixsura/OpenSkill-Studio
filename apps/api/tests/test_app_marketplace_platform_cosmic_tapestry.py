from app.services.app_marketplace_platform_cosmic_tapestry import get_cosmic_tapestry
def test_cosmic_tapestry():
    r = get_cosmic_tapestry()
    assert r["rows_woven"] > 4000
    assert r["unraveling"].startswith("IMPOSSIBLE")
    assert "DORA Elite" in r["pattern"]
    assert "GALAXIES" in r["span"]
    assert "NEVER STOPS" in r["status"]
