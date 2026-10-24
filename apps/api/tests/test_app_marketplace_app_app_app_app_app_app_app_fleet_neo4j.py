from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_neo4j import fleet_neo4j_status
def test_neo4j():
    r = fleet_neo4j_status([{"available": True, "node_count": 1000000, "relationship_count": 5000000}])
    assert r["nodes"] == 1000000
    assert r["healthy"]
