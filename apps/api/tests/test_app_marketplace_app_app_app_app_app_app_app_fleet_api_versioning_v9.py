from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_versioning_v9 import fleet_api_versioning_v9
def test_av_v9():
    r = fleet_api_versioning_v9([{"status": "active"}, {"status": "deprecated"}])
    assert r["active"] == 1
    assert r["sunset"] == 0
    assert r["healthy"]
