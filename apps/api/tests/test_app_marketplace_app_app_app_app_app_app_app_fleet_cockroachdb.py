from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cockroachdb import fleet_cockroachdb_status
def test_crdb():
    r = fleet_cockroachdb_status([{"live": True, "ranges": 10000, "under_replicated": 0}])
    assert r["ranges"] == 10000
    assert r["healthy"]
