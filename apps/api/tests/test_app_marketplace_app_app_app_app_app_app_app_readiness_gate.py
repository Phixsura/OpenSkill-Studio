from app.services.app_marketplace_app_app_app_app_app_app_app_readiness_gate import ReadinessGate

def test_all_ready():
    rg = ReadinessGate()
    rg.register_check("db", lambda: True, critical=True)
    rg.register_check("cache", lambda: True, critical=False)
    r = rg.evaluate()
    assert r["ready"]
    assert r["all_ready"]

def test_critical_fail():
    rg = ReadinessGate()
    rg.register_check("db", lambda: False, critical=True)
    rg.register_check("cache", lambda: True, critical=False)
    r = rg.evaluate()
    assert not r["ready"]
    assert r["passed"] == 1

def test_non_critical_fail():
    rg = ReadinessGate()
    rg.register_check("db", lambda: True, critical=True)
    rg.register_check("metrics", lambda: False, critical=False)
    r = rg.evaluate()
    assert r["ready"]  # critical passed
    assert not r["all_ready"]
