from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_metrics_v5 import fleet_ai_metrics_v5
def test_mv5():
    r = fleet_ai_metrics_v5([{"active": True, "metrics_24h": 5000000000, "series": 500000, "cardinality": 1000000, "resolution_s": 1}])
    assert r["series"] == 500000
    assert r["granular"]
