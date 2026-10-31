from app.services.app_marketplace_platform_genesis_flame import get_genesis_flame
def test_genesis_flame():
    r = get_genesis_flame()
    assert r["eons"] > 4000
    assert r["extinguished"] is False
    assert "commit #1" in r["primordial_fire"]
    assert "inherits" in r["legacy"]
    assert "NEVER STOPS" in r["status"]
