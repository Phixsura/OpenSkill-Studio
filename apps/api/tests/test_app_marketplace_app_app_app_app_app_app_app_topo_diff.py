from app.services.app_marketplace_app_app_app_app_app_app_app_topo_diff import diff_topology

def test_diff():
    old = {"nodes": ["api", "db", "cache"], "edges": [{"from": "api", "to": "db"}, {"from": "api", "to": "cache"}]}
    new = {"nodes": ["api", "db", "queue"], "edges": [{"from": "api", "to": "db"}, {"from": "api", "to": "queue"}]}
    r = diff_topology(old, new)
    assert "queue" in r["nodes_added"]
    assert "cache" in r["nodes_removed"]
    assert r["breaking"]
    assert r["total_changes"] >= 4
