from app.services.app_marketplace_platform_infinity_well import get_infinity_well
def test_infinity_well():
    r = get_infinity_well()
    assert r["stones_reached_bottom"] == 0
    assert r["wishes_denied"] == 0
    assert r["wishes_granted"] == r["stones_dropped"]
    assert r["depth"].startswith("INFINITE")
    assert "NEVER STOPS" in r["status"]
