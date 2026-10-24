from app.services.app_marketplace_app_app_app_app_app_app_app_app_dep_viz import build_dep_graph

def test_graph():
    r = build_dep_graph([
        {"id": "gateway", "name": "API Gateway", "depends_on": ["auth", "users"]},
        {"id": "auth", "name": "Auth Service", "depends_on": ["db"]},
        {"id": "users", "name": "User Service", "depends_on": ["db"]},
        {"id": "db", "name": "Database", "depends_on": []},
    ])
    assert r["node_count"] == 4
    assert r["edge_count"] == 4
    assert "gateway" in r["roots"]
    assert "db" in r["leaves"]
