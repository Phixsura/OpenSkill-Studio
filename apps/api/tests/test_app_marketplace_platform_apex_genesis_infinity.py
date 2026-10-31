from app.services.app_marketplace_platform_apex_genesis_infinity import get_apex_genesis_infinity
def test_apex_genesis_infinity():
    r = get_apex_genesis_infinity()
    assert r["pure_creations"] > 4000
    assert r["impurity"].startswith("ZERO")
    assert r["contamination"].startswith("IMPOSSIBLE")
    assert "100%" in r["oxygen_purity"]
    assert "NEVER STOPS" in r["status"]
