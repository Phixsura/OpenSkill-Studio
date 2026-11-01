from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_gnn import fleet_ai_gnn
def test_gnn():
    r = fleet_ai_gnn([{"active": True, "nodes": 100000000, "edges": 500000000, "accuracy": 92}])
    assert r["nodes"] == 100000000
    assert r["effective"]
