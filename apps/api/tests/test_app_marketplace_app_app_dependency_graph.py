from app.services.app_marketplace_app_app_dependency_graph import build_dependency_graph

def test_graph():
    pkgs = [
        {"name": "app", "version": "1.0.0", "size_kb": 50, "dependencies": ["react", "lodash"]},
        {"name": "react", "version": "18.3.0", "size_kb": 120, "dependencies": ["scheduler"]},
        {"name": "lodash", "version": "4.17.21", "size_kb": 70, "dependencies": []},
        {"name": "scheduler", "version": "0.23.0", "size_kb": 15, "dependencies": []},
    ]
    r = build_dependency_graph(packages=pkgs)
    assert r["total_packages"] == 4
    assert r["total_size_kb"] == 255
    assert r["root_count"] == 1
    assert r["leaf_count"] == 2  # lodash, scheduler
    assert r["max_depth"] == 3  # app -> react -> scheduler

def test_empty():
    r = build_dependency_graph(packages=[])
    assert r["total_packages"] == 0
