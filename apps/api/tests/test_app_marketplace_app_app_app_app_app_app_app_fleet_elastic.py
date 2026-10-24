from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_elastic import fleet_elastic_status
def test_es():
    r = fleet_elastic_status({"status": "yellow", "nodes": 5, "active_shards": 100, "unassigned_shards": 5})
    assert r["unassigned_shards"] == 5
    assert not r["healthy"]
