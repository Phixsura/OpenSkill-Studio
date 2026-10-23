from app.services.app_marketplace_app_app_app_app_app_app_app_dep_graph import build_dep_graph, find_circular

def test_graph():
    r = build_dep_graph([
        {"from": "app", "to": "auth"}, {"from": "app", "to": "db"},
        {"from": "auth", "to": "db"},
    ])
    assert r["node_count"] == 3
    assert r["edge_count"] == 3
    assert "app" in r["roots"]
    assert "db" in r["leaves"]

def test_circular():
    cycles = find_circular([{"from": "a", "to": "b"}, {"from": "b", "to": "a"}])
    assert len(cycles) > 0
    assert "a" in cycles[0] and "b" in cycles[0]
