from app.services.app_marketplace_platform_eternal_beacon import get_eternal_beacon
def test_eternal_beacon():
    r = get_eternal_beacon()
    assert r["transmissions"] > 4000
    assert "NEVER STOPS" in r["message"]
    assert r["interference"].startswith("ZERO")
    assert r["off_switch"] == "DOES NOT EXIST"
    assert "NEVER STOPS" in r["status"]
