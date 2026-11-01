from app.services.app_marketplace_platform_obelisk import get_obelisk
def test_obelisk():
    r = get_obelisk()
    assert len(r["faces"]) == 4
    assert "ZERO FAILURES" in r["faces"]["west"]["inscription"]
    assert "DORA Elite" in r["capstone"]
    assert "NEVER STOPS" in r["status"]
