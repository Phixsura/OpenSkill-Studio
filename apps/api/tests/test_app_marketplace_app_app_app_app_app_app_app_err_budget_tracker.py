from app.services.app_marketplace_app_app_app_app_app_app_app_err_budget_tracker import track_error_budget

def test_healthy():
    r = track_error_budget(app_id="app1", total_requests=1000000, failed_requests=100,
                             elapsed_days=15, period_days=30)
    assert r["status"] == "healthy"
    assert r["remaining_pct"] > 0
    assert r["days_remaining"] == 15

def test_critical():
    r = track_error_budget(app_id="app2", total_requests=1000000, failed_requests=800,
                             elapsed_days=7, period_days=30)
    assert r["status"] == "critical"
    assert r["burn_rate"] > 2
