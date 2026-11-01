from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_revenue import fleet_revenue_metrics
def test_revenue():
    r = fleet_revenue_metrics({"mrr": 50000, "mrr_growth_pct": 15, "avg_ltv": 1200, "avg_cac": 300})
    assert r["arr"] == 600000
    assert r["ltv_cac_ratio"] == 4.0
    assert r["unit_economics_healthy"]
