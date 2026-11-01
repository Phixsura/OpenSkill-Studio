from app.services.app_marketplace_app_app_app_app_app_app_app_service_mesh import create_mesh, find_dependencies

def test_mesh():
    m = create_mesh([
        {"name": "api", "port": 8080, "depends_on": ["auth", "db"]},
        {"name": "auth", "port": 8081, "depends_on": ["db"]},
        {"name": "db", "port": 5432, "healthy": True},
    ])
    assert m["node_count"] == 3
    assert m["connection_count"] == 3
    assert m["healthy"] == 3

def test_deps():
    m = create_mesh([
        {"name": "api", "depends_on": ["auth", "db"]},
        {"name": "auth", "depends_on": ["db"]},
        {"name": "db"},
    ])
    d = find_dependencies(m, "auth")
    assert "db" in d["depends_on"]
    assert "api" in d["depended_by"]
    assert not d["is_leaf"]  # has deps
    assert not d["is_root"]  # has dependents
