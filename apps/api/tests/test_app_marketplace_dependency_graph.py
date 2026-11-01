from app.services.app_marketplace_dependency_graph import build_dependency_graph, detect_circular_dependencies, check_conflicts

def test_graph():
    apps = [
        {"id": "a1", "name": "Auth", "depends_on": [], "conflicts_with": []},
        {"id": "a2", "name": "CRM", "depends_on": ["a1"], "conflicts_with": []},
    ]
    g = build_dependency_graph(apps=apps)
    assert g["node_count"] == 2
    assert g["edge_count"] == 1

def test_circular():
    edges = [{"from": "a", "to": "b", "type": "depends_on"},
             {"from": "b", "to": "c", "type": "depends_on"},
             {"from": "c", "to": "a", "type": "depends_on"}]
    cycles = detect_circular_dependencies(edges=edges)
    assert len(cycles) > 0

def test_no_circular():
    edges = [{"from": "a", "to": "b", "type": "depends_on"}]
    cycles = detect_circular_dependencies(edges=edges)
    assert len(cycles) == 0

def test_conflicts():
    installed = [{"id": "a1", "name": "OldCRM", "conflicts_with": []}]
    new = {"id": "a2", "name": "NewCRM", "conflicts_with": ["a1"]}
    r = check_conflicts(installed_apps=installed, new_app=new)
    assert r["has_conflicts"]

def test_no_conflicts():
    r = check_conflicts(installed_apps=[{"id": "a1", "name": "X", "conflicts_with": []}],
                         new_app={"id": "a2", "conflicts_with": []})
    assert not r["has_conflicts"]
