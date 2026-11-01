from app.services.app_marketplace_app_app_network_graph import build_network_graph

def test_graph():
    nodes = [{"id": "api", "label": "API Gateway"}, {"id": "auth", "label": "Auth"},
             {"id": "db", "label": "Database"}]
    edges = [{"from": "api", "to": "auth"}, {"from": "api", "to": "db"},
             {"from": "auth", "to": "db"}]
    r = build_network_graph(nodes=nodes, edges=edges)
    assert r["node_count"] == 3
    assert r["edge_count"] == 3
    assert r["root_count"] == 1  # api
    assert r["leaf_count"] == 1  # db

def test_empty():
    r = build_network_graph(nodes=[], edges=[])
    assert r["node_count"] == 0
