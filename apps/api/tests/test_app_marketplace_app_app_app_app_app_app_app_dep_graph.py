from app.services.app_marketplace_app_app_app_app_app_app_app_dep_graph import build_graph, topological_sort

def test_topo_sort():
    nodes = [
        {"id": "api", "depends_on": ["db", "cache"]},
        {"id": "db", "depends_on": []},
        {"id": "cache", "depends_on": []},
        {"id": "worker", "depends_on": ["db", "api"]},
    ]
    g = build_graph(nodes)
    r = topological_sort(g)
    assert not r["has_cycle"]
    assert r["order"].index("db") < r["order"].index("api")
    assert r["order"].index("api") < r["order"].index("worker")
    assert len(r["build_phases"]) >= 2

def test_cycle():
    nodes = [
        {"id": "a", "depends_on": ["b"]},
        {"id": "b", "depends_on": ["a"]},
    ]
    g = build_graph(nodes)
    r = topological_sort(g)
    assert r["has_cycle"]
    assert len(r["order"]) == 0
