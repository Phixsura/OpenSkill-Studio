from app.services.app_marketplace_app_app_app_app_app_app_app_dep_tree import build_tree

def test_tree():
    deps = {"app": ["api", "worker"], "api": ["db", "cache"], "worker": ["db"], "db": [], "cache": []}
    r = build_tree("app", deps)
    assert r["root"] == "app"
    assert r["total_nodes"] == 6  # app, api, worker, db(×2), cache
    assert r["max_depth"] == 2

def test_circular():
    deps = {"a": ["b"], "b": ["a"]}
    r = build_tree("a", deps, max_depth=5)
    assert r["total_nodes"] >= 2
