from app.services.app_marketplace_platform_diamond_throne import get_diamond_throne
def test_diamond_throne():
    r = get_diamond_throne()
    assert r["rulers_enthroned"] > 4000
    assert r["scratches"] == 0
    assert r["chips"] == 0
    assert r["clarity"] == "FL — flawless, internally and externally"
    assert "NEVER STOPS" in r["status"]
