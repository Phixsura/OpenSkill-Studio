from app.services.app_marketplace_platform_pinnacle import get_pinnacle
def test_pinnacle():
    r = get_pinnacle()
    assert r["falls"] == 0
    assert r["ascents"] > 4000
    assert "DORA Elite" in r["flag"]
    assert r["air_quality"].startswith("PURE")
    assert "NEVER STOPS" in r["status"]
