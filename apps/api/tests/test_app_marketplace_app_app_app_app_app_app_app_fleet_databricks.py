from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_databricks import fleet_databricks_status
def test_db():
    r = fleet_databricks_status([{"status": "RUNNING", "clusters": 10, "dbu_24h": 500}])
    assert r["clusters"] == 10
    assert r["all_running"]
