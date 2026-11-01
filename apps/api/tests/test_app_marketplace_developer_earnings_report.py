from app.services.app_marketplace_developer_earnings_report import build_earnings_report

def test_report():
    data = [
        {"month": "2026-08", "gross": 1000, "fees": 300},
        {"month": "2026-09", "gross": 1500, "fees": 450},
        {"month": "2026-10", "gross": 2000, "fees": 600},
    ]
    r = build_earnings_report(developer_id="d1", monthly_data=data)
    assert r["total_gross"] == 4500
    assert r["total_fees"] == 1350
    assert r["total_net"] == 3150
    assert r["best_month"] == "2026-10"
    assert r["avg_growth_pct"] > 0

def test_empty():
    r = build_earnings_report(developer_id="d1", monthly_data=[])
    assert r["total_net"] == 0
    assert r["best_month"] is None
