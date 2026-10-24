from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sbom_tracker_v9 import fleet_sbom_tracker_v9
def test_sbom_v9():
    r = fleet_sbom_tracker_v9([{"sbom_generated": True, "license_compliant": True, "components": 200}])
    assert r["with_sbom"] == 1
    assert r["healthy"]
