from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_puppet import fleet_puppet_status
def test_puppet():
    r = fleet_puppet_status([{"status": "unchanged"}, {"status": "changed"}, {"status": "failed"}])
    assert r["in_sync"] == 1
    assert not r["converged"]
