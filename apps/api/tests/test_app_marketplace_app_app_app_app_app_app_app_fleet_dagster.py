from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dagster import fleet_dagster_status
def test_dg():
    r = fleet_dagster_status([{"status": "running", "assets": 200, "materializations_24h": 5000}])
    assert r["assets"] == 200
    assert r["active"]
