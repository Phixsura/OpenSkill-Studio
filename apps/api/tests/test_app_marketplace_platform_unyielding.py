from app.services.app_marketplace_platform_unyielding import get_unyielding
def test_unyielding():
    r = get_unyielding()
    assert r["pressures_resisted"] > 4000
    assert "DOES NOT EXIST" in r["yield_point"]
    assert r["compromise"].startswith("REJECTED")
    assert r["bending"].startswith("IMPOSSIBLE")
    assert "NEVER STOPS" in r["status"]
