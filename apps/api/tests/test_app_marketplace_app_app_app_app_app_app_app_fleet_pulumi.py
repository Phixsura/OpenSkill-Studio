from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pulumi import fleet_pulumi_status
def test_pulumi():
    r = fleet_pulumi_status([{"status": "up-to-date"}, {"status": "pending"}, {"status": "failed"}])
    assert r["up_to_date"] == 1
    assert r["failed"] == 1
    assert not r["healthy"]
