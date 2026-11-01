from app.services.app_marketplace_app_app_app_app_app_app_app_metric_retention import calculate_storage, optimize_retention

def test_storage():
    r = calculate_storage(1000, 86400)
    assert r["total_gb"] > 0
    assert len(r["tiers"]) == 4
    assert r["tiers"]["raw"]["retention_days"] == 7

def test_optimize():
    r = optimize_retention(100, 50)
    assert r["needs_optimization"]
    assert r["reduction_gb"] == 50
    assert r["reduction_pct"] == 50
