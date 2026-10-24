from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_multicluster import fleet_multicluster
def test_multi():
    r = fleet_multicluster([{"status": "healthy"}, {"status": "healthy"}, {"status": "degraded"}])
    assert r["healthy"] == 2
    assert not r["all_ok"]
