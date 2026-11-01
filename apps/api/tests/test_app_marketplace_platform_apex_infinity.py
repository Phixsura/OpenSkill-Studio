from app.services.app_marketplace_platform_apex_infinity import get_apex_infinity
def test_apex_infinity():
    r = get_apex_infinity()
    assert r["steps_taken"] > 4000
    assert "DOES NOT EXIST" in r["summit"]
    assert r["fatigue"].startswith("ZERO")
    assert "roped together" in r["climbing_partner"]
    assert "NEVER STOPS" in r["status"]
