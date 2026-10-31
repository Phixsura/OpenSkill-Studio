from app.services.app_marketplace_app_app_revenue_dashboard import build_revenue_dashboard

def test_dashboard():
    data = [
        {"month": "2026-08", "revenue": 5000, "fees": 1500},
        {"month": "2026-09", "revenue": 6000, "fees": 1800},
        {"month": "2026-10", "revenue": 7200, "fees": 2160},
    ]
    r = build_revenue_dashboard(monthly_data=data)
    assert r["total_revenue"] == 18200
    assert r["mrr"] == 7200
    assert r["arr"] == 86400
    assert r["avg_monthly_growth"] == 20.0
    assert r["months"] == 3

def test_empty():
    r = build_revenue_dashboard(monthly_data=[])
    assert "error" in r
