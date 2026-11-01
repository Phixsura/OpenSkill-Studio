from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_loki import fleet_loki_status
def test_loki():
    r = fleet_loki_status([{"healthy": True, "ingestion_mb_per_sec": 50, "query_avg_ms": 200}])
    assert r["ingestion_mb_per_sec"] == 50
    assert r["all_healthy"]
