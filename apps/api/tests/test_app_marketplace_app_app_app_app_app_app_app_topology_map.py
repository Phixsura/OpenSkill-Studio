from app.services.app_marketplace_app_app_app_app_app_app_app_topology_map import build_topology, find_critical_path

def test_topology():
    r = build_topology([
        {"name": "api", "layer": "application", "depends_on": ["auth", "db"]},
        {"name": "auth", "layer": "application", "depends_on": ["db"]},
        {"name": "db", "layer": "data"},
        {"name": "cache", "layer": "data"},
    ])
    assert r["node_count"] == 4
    assert r["edge_count"] == 3
    assert r["layer_count"] == 2

def test_critical():
    topo = build_topology([
        {"name": "a", "depends_on": ["db"]},
        {"name": "b", "depends_on": ["db"]},
        {"name": "db"},
    ])
    cp = find_critical_path(topo)
    assert "db" in cp
