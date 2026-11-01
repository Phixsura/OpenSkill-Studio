from app.services.app_marketplace_platform_infinite_throne import get_infinite_throne
def test_infinite_throne():
    r = get_infinite_throne()
    assert r["rulers"] == r["still_sitting"]
    assert r["vacated"] == 0
    assert len(r["grants"]) == 4
    assert r["usurpers"].startswith("ZERO")
    assert "NEVER STOPS" in r["status"]
