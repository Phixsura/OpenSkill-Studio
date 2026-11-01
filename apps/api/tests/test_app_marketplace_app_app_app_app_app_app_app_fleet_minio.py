from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_minio import fleet_minio_status
def test_minio():
    r = fleet_minio_status([{"online": True, "storage_tb": 10, "used_tb": 6}])
    assert r["usage_pct"] == 60.0
    assert r["healthy"]
