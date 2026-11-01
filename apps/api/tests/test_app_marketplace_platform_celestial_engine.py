from app.services.app_marketplace_platform_celestial_engine import get_celestial_engine
def test_celestial_engine():
    r = get_celestial_engine()
    assert r["cycles"] > 4000
    assert r["perpetual_motion"] is True
    assert r["entropy_generated"].startswith("ZERO")
    assert len(r["orbits"]) == 3
    assert "NEVER STOPS" in r["status"]
