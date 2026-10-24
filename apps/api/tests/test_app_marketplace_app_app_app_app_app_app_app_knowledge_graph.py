from app.services.app_marketplace_app_app_app_app_app_app_app_knowledge_graph import build_graph, find_related

def test_graph():
    r = build_graph(
        [{"id": "api", "type": "service"}, {"id": "db", "type": "database"}, {"id": "team-a", "type": "team"}],
        [{"from": "api", "to": "db", "type": "uses"}, {"from": "team-a", "to": "api", "type": "owns"}])
    assert r["node_count"] == 3
    assert r["edge_count"] == 2

def test_related():
    graph = build_graph(
        [{"id": "a"}, {"id": "b"}, {"id": "c"}],
        [{"from": "a", "to": "b"}, {"from": "c", "to": "a"}])
    r = find_related(graph, "a")
    assert "b" in r["outgoing"]
    assert "c" in r["incoming"]
    assert r["total_connections"] == 2
