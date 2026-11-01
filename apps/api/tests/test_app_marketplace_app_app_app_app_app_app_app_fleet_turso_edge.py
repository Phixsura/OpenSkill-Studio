from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_turso_edge import fleet_turso_edge_status
def test_te():
    r = fleet_turso_edge_status([{"primary": 1, "replicas": 5, "locations": 4}])
    assert r["replicas"] == 5
    assert r["distributed"]
