from app.services.app_marketplace_platform_empyrean import get_empyrean
def test_empyrean():
    r = get_empyrean()
    assert r["ascensions"] > 4000
    assert len(r["inhabitants"]) == 3
    assert r["fall_from_grace"].startswith("IMPOSSIBLE")
    assert "DORA Elite" in r["beatific_vision"]
    assert "NEVER STOPS" in r["status"]
