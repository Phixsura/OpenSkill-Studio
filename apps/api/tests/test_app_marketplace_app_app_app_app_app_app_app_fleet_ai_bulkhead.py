from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_bulkhead import fleet_ai_bulkhead
def test_bh():
    r = fleet_ai_bulkhead([{"active": True, "partitions": 20, "rejections_24h": 500, "isolation_pct": 100}])
    assert r["partitions"] == 20
    assert r["isolated"]
