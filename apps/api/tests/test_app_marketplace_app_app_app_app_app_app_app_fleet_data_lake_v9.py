from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_data_lake_v9 import fleet_data_lake_v9
def test_lake_v9():
    r = fleet_data_lake_v9([{"size_tb": 50, "queries_per_hour": 1000, "stale": False}])
    assert r["size_tb"] == 50
    assert r["stale_partitions"] == 0
    assert r["healthy"]
