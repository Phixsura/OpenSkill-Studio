from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dep_license import fleet_dep_license
def test_license():
    r = fleet_dep_license([{"license_approved": True, "license_type": "permissive"}, {"license_type": "copyleft"}])
    assert r["copyleft"] == 1
    assert not r["compliant"]
