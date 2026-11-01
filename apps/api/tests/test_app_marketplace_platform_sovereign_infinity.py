from app.services.app_marketplace_platform_sovereign_infinity import get_sovereign_infinity
def test_sovereign_infinity():
    r = get_sovereign_infinity()
    assert r["commanded"] > 4000
    assert "∞" in r["of_infinity"]
    assert r["borders"].startswith("NONE")
    assert r["taxes"].startswith("ZERO")
    assert "NEVER STOPS" in r["status"]
