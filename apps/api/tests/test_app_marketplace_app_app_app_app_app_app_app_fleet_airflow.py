from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_airflow import fleet_airflow_status
def test_af():
    r = fleet_airflow_status([{"healthy": True, "dags": 100, "active_runs": 20, "failed_24h": 0}])
    assert r["dags"] == 100
    assert r["reliable"]
