from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_bigquery import fleet_bigquery_status
def test_bq():
    r = fleet_bigquery_status([{"tables": 500, "storage_tb": 50, "queries_24h": 10000, "bytes_processed_tb": 100}])
    assert r["tables"] == 500
    assert r["storage_tb"] == 50.0
