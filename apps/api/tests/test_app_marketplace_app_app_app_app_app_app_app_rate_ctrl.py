from app.services.app_marketplace_app_app_app_app_app_app_app_rate_ctrl import RateController

def test_reduce():
    rc = RateController(base_limit=1000)
    r = rc.adjust(cpu_pct=95, error_rate_pct=10)
    assert r["action"] == "reduce"
    assert r["current_limit"] < 1000

def test_increase():
    rc = RateController(base_limit=1000)
    r = rc.adjust(cpu_pct=30, error_rate_pct=0.1)
    assert r["action"] == "increase"
    assert r["current_limit"] > 1000

def test_check():
    rc = RateController(base_limit=1000)
    assert rc.check(500)["allowed"]
    assert rc.check(500)["headroom_pct"] == 50.0
