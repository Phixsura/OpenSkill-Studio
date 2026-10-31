from app.services.app_marketplace_platform_vanguard import get_vanguard
def test_vanguard():
    r = get_vanguard()
    assert r["charges_led"] == 4096
    assert "2^12" in r["power_of_two"]
    assert r["retreats"] == 0
    assert r["casualties"] == 0
    assert "NEVER STOPS" in r["status"]
