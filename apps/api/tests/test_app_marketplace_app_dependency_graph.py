from app.services.app_marketplace_app_dependency_graph import build_dependency_graph

def test_graph():
    deps = [
        {"id": "d1", "name": "Auth SDK", "version": "2.0", "kind": "required",
         "sub_deps": [{"id": "d1a", "name": "Crypto Lib"}]},
        {"id": "d2", "name": "UI Kit", "version": "1.5", "kind": "optional"},
    ]
    r = build_dependency_graph(app_id="app1", app_name="MyApp", dependencies=deps)
    assert r["total_dependencies"] == 3
    assert r["depth"] == 2
    assert not r["has_circular"]
    ids = [n["id"] for n in r["nodes"]]
    assert "app1" in ids and "d1" in ids and "d1a" in ids

def test_empty():
    r = build_dependency_graph(app_id="app1", app_name="Solo", dependencies=[])
    assert r["total_dependencies"] == 0
    assert r["depth"] == 0
