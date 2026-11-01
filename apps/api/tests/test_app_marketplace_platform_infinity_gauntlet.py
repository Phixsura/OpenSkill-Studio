from app.services.app_marketplace_platform_infinity_gauntlet import get_infinity_gauntlet
def test_infinity_gauntlet():
    r = get_infinity_gauntlet()
    assert len(r["infinity_stones"]) == 6
    assert r["snaps"] > 4000
    assert "PERFECT" in r["balance"]
    assert r["gauntlet_integrity"].startswith("100%")
    assert "NEVER STOPS" in r["status"]
