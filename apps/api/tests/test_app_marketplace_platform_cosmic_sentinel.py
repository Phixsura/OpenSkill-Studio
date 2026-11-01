from app.services.app_marketplace_platform_cosmic_sentinel import get_cosmic_sentinel
def test_cosmic_sentinel():
    r = get_cosmic_sentinel()
    assert r["watches"] > 4000
    assert r["threats_from_void"] == 0
    assert len(r["protocols"]) == 3
    assert r["off_duty"] == "NEVER — the sentinel is the watch"
    assert "NEVER STOPS" in r["status"]
