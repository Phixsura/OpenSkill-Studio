from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dbt import fleet_dbt_status
def test_dbt():
    r = fleet_dbt_status([{"last_run_status": "success", "models": 200, "tests": 500}])
    assert r["models"] == 200
    assert r["healthy"]
