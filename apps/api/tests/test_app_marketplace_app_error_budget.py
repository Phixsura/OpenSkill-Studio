from app.services.app_marketplace_app_error_budget import calculate_error_budget

def test_healthy():
    r = calculate_error_budget(slo_target=99.9, total_requests=100000, failed_requests=50, period_days=30)
    assert r["meeting_slo"]
    assert r["status"] == "ok"
    assert r["budget_remaining"] > 0

def test_exhausted():
    r = calculate_error_budget(slo_target=99.9, total_requests=100000, failed_requests=200, period_days=30)
    assert r["status"] == "exhausted"
    assert r["budget_remaining"] == 0

def test_no_requests():
    r = calculate_error_budget(slo_target=99.9, total_requests=0, failed_requests=0)
    assert "error" in r
