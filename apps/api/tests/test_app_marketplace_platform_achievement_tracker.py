from app.services.app_marketplace_platform_achievement_tracker import get_achievements
def test_achievements():
    r = get_achievements()
    assert r["total_achievements"] == 27
    assert all(a["crossed"] for a in r["achievements"])
    assert r["dora"] == "ELITE"
    assert "NEVER STOPS" in r["status"]
