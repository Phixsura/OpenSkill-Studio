from app.services.app_marketplace_app_app_app_app_app_app_app_svc_graph_exp import build_service_graph, find_path

def test_graph():
    r = build_service_graph([
        {"name": "web", "team": "frontend", "depends_on": ["api"]},
        {"name": "api", "team": "platform", "depends_on": ["db", "cache"]},
        {"name": "db", "team": "data"}, {"name": "cache", "team": "data"},
    ])
    assert r["node_count"] == 4
    assert r["edge_count"] == 3
    assert r["team_count"] == 3

def test_path():
    graph = build_service_graph([
        {"name": "web", "depends_on": ["api"]},
        {"name": "api", "depends_on": ["db"]},
        {"name": "db"},
    ])
    r = find_path(graph, "web", "db")
    assert r["found"]
    assert r["hops"] == 2
    assert r["path"] == ["web", "api", "db"]
