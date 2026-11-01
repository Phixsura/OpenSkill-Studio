from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_victoriametrics import fleet_vm_status
def test_vm():
    r = fleet_vm_status([{"healthy": True, "rows_inserted_per_sec": 1000000, "storage_gb": 500}])
    assert r["rows_per_sec"] == 1000000
    assert r["all_healthy"]
