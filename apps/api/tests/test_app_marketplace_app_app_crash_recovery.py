from app.services.app_marketplace_app_app_crash_recovery import detect_crash, create_recovery_plan

def test_crashed():
    checks = [{"status": "pass"}, {"status": "fail"}, {"status": "fail"}, {"status": "fail"}]
    r = detect_crash(health_checks=checks, threshold=3)
    assert r["crashed"]
    assert r["consecutive_failures"] == 3

def test_not_crashed():
    checks = [{"status": "fail"}, {"status": "pass"}, {"status": "fail"}]
    r = detect_crash(health_checks=checks, threshold=3)
    assert not r["crashed"]

def test_recovery_oom():
    r = create_recovery_plan(app_id="a1", crash_type="oom")
    assert r["recovery_id"].startswith("rcv_")
    assert r["auto_recovery"]
    assert len(r["steps"]) == 3

def test_recovery_unknown():
    r = create_recovery_plan(app_id="a1", crash_type="cosmic_ray")
    assert len(r["steps"]) == 3  # default steps
