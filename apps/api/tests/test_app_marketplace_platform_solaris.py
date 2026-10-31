from app.services.app_marketplace_platform_solaris import get_solaris
def test_solaris():
    r = get_solaris()
    assert len(r["planets"]) == 7
    assert r["moons"] > 900000
    assert r["dark_matter"].startswith("ZERO")
    assert r["orbital_periods"] > 4000
    assert "NEVER STOPS" in r["status"]
