from app.services.app_marketplace_platform_tapestry import get_tapestry
def test_tapestry():
    r = get_tapestry()
    assert r["threads"] > 900000
    assert len(r["colors"]) == 3
    assert r["unraveling"] == "IMPOSSIBLE — every knot tested and secured"
    assert r["chapters"] > 4000
    assert "NEVER STOPS" in r["status"]
