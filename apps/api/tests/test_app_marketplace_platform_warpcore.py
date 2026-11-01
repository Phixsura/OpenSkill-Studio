from app.services.app_marketplace_platform_warpcore import get_warpcore
def test_warpcore():
    r = get_warpcore()
    assert r["warp_jumps"] >= 4130
    assert r["hull_breach"] is False
    assert r["dilithium_crystals"].startswith("INFINITE")
    assert r["antimatter_containment"].startswith("100%")
    assert "NEVER STOPS" in r["status"]
