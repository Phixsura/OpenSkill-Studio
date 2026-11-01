from app.services.app_marketplace_platform_valkyrie import get_valkyrie
def test_valkyrie():
    r = get_valkyrie()
    assert r["warriors_left_behind"] == 0
    assert r["selections"] > 4000
    assert r["odin_approval"] == "GRANTED — the all-father is pleased"
    assert "PREVENTED" in r["ragnarok"]
    assert "NEVER STOPS" in r["status"]
