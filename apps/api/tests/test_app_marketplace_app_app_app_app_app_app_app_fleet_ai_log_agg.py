from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_log_agg import fleet_ai_log_aggregator
def test_la():
    r = fleet_ai_log_aggregator([{"active": True, "logs_24h": 500000000, "storage_gb": 5000, "sources": 200}])
    assert r["logs_24h"] == 500000000
    assert r["collecting"]
