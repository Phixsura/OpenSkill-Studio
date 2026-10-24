from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rds import fleet_rds_status
def test_rds():
    r = fleet_rds_status([{"status": "available", "multi_az": True, "storage_gb": 500}])
    assert r["multi_az"] == 1
    assert r["all_available"]
