from app.services.app_comparison import compare_apps

A = {"id": "a1", "name": "App A", "category": "connector", "permissions": ["read:cohorts", "write:cohorts"], "install_count": 100}
B = {"id": "b1", "name": "App B", "category": "automation", "permissions": ["read:cohorts", "subscribe:events"], "install_count": 200}

def test_basic():
    r = compare_apps(A, B)
    assert r["app_a"]["name"] == "App A"
    assert r["app_b"]["name"] == "App B"

def test_differences():
    r = compare_apps(A, B)
    assert "category" in r["differences"]

def test_permissions():
    r = compare_apps(A, B)
    assert "write:cohorts" in r["permissions"]["only_a"]
    assert "subscribe:events" in r["permissions"]["only_b"]
    assert "read:cohorts" in r["permissions"]["shared"]

def test_installs():
    r = compare_apps(A, B)
    assert r["install_comparison"]["a"] == 100
    assert r["install_comparison"]["b"] == 200
