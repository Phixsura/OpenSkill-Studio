from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_clickhouse import fleet_clickhouse_status
def test_ch():
    r = fleet_clickhouse_status([{"healthy": True, "total_rows": 1000000000, "qps": 500}])
    assert r["total_rows"] == 1000000000
    assert r["all_healthy"]
