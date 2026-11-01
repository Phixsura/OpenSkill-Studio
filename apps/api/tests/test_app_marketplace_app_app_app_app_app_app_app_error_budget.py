from app.services.app_marketplace_app_app_app_app_app_app_app_error_budget import calculate_error_budget

def test_healthy():
    r = calculate_error_budget(slo_target=99.9, total_requests=1000000,
                                failed_requests=100, elapsed_hours=360, period_hours=720)
    assert r["budget_total"] == 999
    assert r["consumed_pct"] == 10.0
    assert r["remaining_pct"] == 90.0
    assert r["status"] == "healthy"
    assert r["burn_rate"] < 1

def test_critical():
    r = calculate_error_budget(slo_target=99.9, total_requests=1000000,
                                failed_requests=800, elapsed_hours=180, period_hours=720)
    assert r["consumed_pct"] == 80.1
    assert r["burn_rate"] > 2
    assert r["status"] == "critical"
