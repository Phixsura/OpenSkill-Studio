from app.services.app_marketplace_app_app_rate_plan import get_rate_plan, check_usage

def test_get_plan():
    r = get_rate_plan(plan_id="pro")
    assert r["rpm"] == 1000
    assert r["rpd"] == 100000

def test_unknown():
    r = get_rate_plan(plan_id="platinum")
    assert "error" in r

def test_check_normal():
    r = check_usage(plan_id="pro", current_rpm=500, current_rpd=50000)
    assert not r["throttled"]
    assert not r["upgrade_suggested"]

def test_check_throttled():
    r = check_usage(plan_id="free", current_rpm=60, current_rpd=500)
    assert r["throttled"]
