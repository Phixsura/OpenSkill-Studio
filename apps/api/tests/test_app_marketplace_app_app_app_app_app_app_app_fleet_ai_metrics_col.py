from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_metrics_col import fleet_ai_metrics_collector
def test_mc():
    r = fleet_ai_metrics_collector([{"active": True, "metrics_24h": 1000000000, "series": 50000, "resolution_s": 5}])
    assert r["series"] == 50000
    assert r["granular"]
