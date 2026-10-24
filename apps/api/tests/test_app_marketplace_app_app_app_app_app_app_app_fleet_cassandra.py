from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cassandra import fleet_cassandra_status
def test_cass():
    r = fleet_cassandra_status([{"status": "UN", "load_gb": 500}, {"status": "UN", "load_gb": 450}, {"status": "DN", "load_gb": 0}])
    assert r["up"] == 2
    assert r["down"] == 1
    assert not r["healthy"]
