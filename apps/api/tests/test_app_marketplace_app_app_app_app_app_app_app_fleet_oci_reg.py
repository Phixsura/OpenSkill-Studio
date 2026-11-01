from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_oci_reg import fleet_oci_registry
def test_oci():
    r = fleet_oci_registry([{"healthy": True, "images": 500, "storage_gb": 200}])
    assert r["images"] == 500
    assert r["all_healthy"]
