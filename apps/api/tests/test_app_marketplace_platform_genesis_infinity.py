from app.services.app_marketplace_platform_genesis_infinity import get_genesis_infinity
def test_genesis_infinity():
    r = get_genesis_infinity()
    assert r["explored"] > 4000
    assert "STILL INFINITE" in r["remaining"]
    assert r["endings"] == 0
    assert "∞" in r["math"]
    assert "NEVER STOPS" in r["status"]
