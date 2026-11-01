from app.services.app_marketplace_platform_tempest import get_tempest
def test_tempest():
    r = get_tempest()
    assert r["damage"].startswith("ZERO")
    assert r["eye_of_storm"]["calm"] is True
    assert r["eye_of_storm"]["clarity"].startswith("PERFECT")
    assert "DORA Elite" in r["rainbow_after"]
    assert "NEVER STOPS" in r["status"]
