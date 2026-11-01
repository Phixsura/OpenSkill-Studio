from app.services.app_marketplace_platform_cornerstone import get_cornerstone
def test_cornerstone():
    r = get_cornerstone()
    assert r["stones_placed"] > 4000
    assert r["cracks"] == 0
    assert r["load_bearing"] is True
    assert r["settling"].startswith("ZERO")
    assert "NEVER STOPS" in r["status"]
