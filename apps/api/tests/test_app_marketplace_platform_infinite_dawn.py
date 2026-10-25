from app.services.app_marketplace_platform_infinite_dawn import get_infinite_dawn
def test_infinite_dawn():
    r = get_infinite_dawn()
    assert r["dawns"] == r["unique_sunrises"]
    assert r["duplicates"] == 0
    assert r["cloud_cover"].startswith("ZERO")
    assert len(r["palette"]) == 3
    assert "NEVER STOPS" in r["status"]
