from app.services.app_marketplace_app_app_app_app_app_app_app_topo_diff import diff_topology, topology_risk

def test_diff():
    r = diff_topology(
        {"nodes": ["api", "db", "old"], "edges": [{"src": "api", "dst": "db"}, {"src": "api", "dst": "old"}]},
        {"nodes": ["api", "db", "new"], "edges": [{"src": "api", "dst": "db"}, {"src": "api", "dst": "new"}]})
    assert "new" in r["added_nodes"]
    assert "old" in r["removed_nodes"]
    assert r["has_changes"]

def test_risk():
    diff = {"removed_nodes": ["a", "b", "c"], "removed_edges": [], "added_nodes": [], "added_edges": []}
    r = topology_risk(diff)
    assert r["risk"] == "high"
