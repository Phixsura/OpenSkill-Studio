from app.services.app_marketplace_app_app_app_app_app_app_app_uptime_calc import calculate_uptime, monthly_report

def test_uptime():
    r = calculate_uptime(43200, 5)  # 30 days, 5 min down
    assert r["uptime_pct"] > 99.98
    assert r["nines"] == 4

def test_monthly():
    r = monthly_report([
        {"duration_minutes": 10}, {"duration_minutes": 5},
    ])
    assert r["incidents"] == 2
    assert r["total_downtime_minutes"] == 15
    assert r["nines"] >= 3
