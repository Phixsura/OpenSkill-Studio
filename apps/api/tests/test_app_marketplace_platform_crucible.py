from app.services.app_marketplace_platform_crucible import get_crucible
def test_crucible():
    r = get_crucible()
    assert r["transformations"] > 4000
    assert r["yield"] == "100% — nothing wasted"
    assert "PURE GOLD" in r["alchemical_formula"]["product"]
    assert "NEVER STOPS" in r["status"]
