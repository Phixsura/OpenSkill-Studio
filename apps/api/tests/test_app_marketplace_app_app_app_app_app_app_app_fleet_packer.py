from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_packer import fleet_packer_status
def test_packer():
    r = fleet_packer_status([{"status": "succeeded", "duration_min": 20}, {"status": "failed"}])
    assert r["succeeded"] == 1
    assert not r["reliable"]
