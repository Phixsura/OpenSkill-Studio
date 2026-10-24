from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_ver import fleet_api_versions
def test_versions():
    r = fleet_api_versions([{"version": "v1", "deprecated": True}, {"version": "v2"}, {"version": "v2"}])
    assert r["versions"]["v2"] == 2
    assert r["deprecated"] == 1
    assert r["needs_migration"]
