from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dep_graph import fleet_ai_dependency_graph
def test_dg():
    r = fleet_ai_dependency_graph([{"active": True, "services": 200, "edges": 1000, "circular": 0}])
    assert r["services"] == 200
    assert r["healthy"]
