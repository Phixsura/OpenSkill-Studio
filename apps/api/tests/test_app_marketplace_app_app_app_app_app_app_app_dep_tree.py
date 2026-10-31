from app.services.app_marketplace_app_app_app_app_app_app_app_dep_tree import build_tree, find_circular

def test_tree():
    r = build_tree([
        {"parent": "api", "child": "auth"},
        {"parent": "api", "child": "db"},
        {"parent": "auth", "child": "db"},
    ])
    assert r["roots"] == ["api"]
    assert r["max_depth"] == 3
    assert r["edges"] == 3

def test_circular():
    cycles = find_circular([
        {"parent": "a", "child": "b"},
        {"parent": "b", "child": "c"},
        {"parent": "c", "child": "a"},
    ])
    assert len(cycles) >= 1
