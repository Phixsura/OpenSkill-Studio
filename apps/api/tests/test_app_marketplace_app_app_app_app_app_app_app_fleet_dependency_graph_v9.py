from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dependency_graph_v9 import fleet_dependency_graph_v9
def test_dep_v9():
    r = fleet_dependency_graph_v9([{"depends_on": ["a", "b"]}, {"depends_on": ["c"]}])
    assert r["edges"] == 3
    assert r["circular_deps"] == 0
    assert r["healthy"]
