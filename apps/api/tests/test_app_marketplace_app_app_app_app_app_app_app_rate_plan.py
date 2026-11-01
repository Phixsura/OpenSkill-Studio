from app.services.app_marketplace_app_app_app_app_app_app_app_rate_plan import get_plan, check_usage

def test_get():
    r = get_plan("pro")
    assert r["found"]
    assert r["limits"]["rpm"] == 1000

def test_check():
    r = check_usage("free", current_daily=900, current_monthly=5000)
    assert r["daily_pct"] == 90.0
    assert r["recommend_upgrade"]
    assert not r["exceeded"]

def test_exceeded():
    r = check_usage("free", current_daily=1500, current_monthly=5000)
    assert r["exceeded"]
