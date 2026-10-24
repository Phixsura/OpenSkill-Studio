from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_prefect import fleet_prefect_status
def test_pf():
    r = fleet_prefect_status([{"is_schedule_active": True, "completed_24h": 100, "failed_24h": 0}])
    assert r["completed_24h"] == 100
    assert r["reliable"]
