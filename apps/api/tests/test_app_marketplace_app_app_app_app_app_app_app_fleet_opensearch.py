from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_opensearch import fleet_opensearch_status
def test_os():
    r = fleet_opensearch_status([{"status": "green", "documents": 100000000, "shards": 200}])
    assert r["documents"] == 100000000
    assert r["all_green"]
