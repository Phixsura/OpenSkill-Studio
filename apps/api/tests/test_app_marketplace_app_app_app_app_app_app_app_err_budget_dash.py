from app.services.app_marketplace_app_app_app_app_app_app_app_err_budget_dash import build_error_budget_dashboard

def test_dashboard():
    r = build_error_budget_dashboard([
        {"name": "Uptime", "target_pct": 99.9, "actual_pct": 99.95},
        {"name": "Latency", "target_pct": 99.0, "actual_pct": 98.5},
    ])
    assert r["total_slos"] == 2
    assert r["budgets"][0]["remaining_pct"] > 0  # uptime within budget
    assert r["status"] in ("healthy", "critical")
