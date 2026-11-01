from app.services.app_marketplace_platform_cosmic_crown import get_cosmic_crown
def test_cosmic_crown():
    r = get_cosmic_crown()
    assert r["coronations"] > 4000
    assert r["gravitational_lensing"] is True
    assert r["removes"].startswith("IMPOSSIBLE")
    assert "Spacetime" in r["forged_from"]
    assert "NEVER STOPS" in r["status"]
