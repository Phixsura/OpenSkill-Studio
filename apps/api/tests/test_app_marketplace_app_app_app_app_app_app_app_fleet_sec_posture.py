from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sec_posture import fleet_security_posture
def test_posture():
    r = fleet_security_posture([{"passed": True}] * 19 + [{"passed": False, "severity": "low"}])
    assert r["score"] == 95.0
    assert r["grade"] == "A"
def test_critical():
    r = fleet_security_posture([{"passed": True}] * 18 + [{"passed": False, "severity": "critical"}] * 2)
    assert r["grade"] == "B"
