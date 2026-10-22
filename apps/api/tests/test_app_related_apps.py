from app.services.app_related_apps import find_related

APP = {"id": "a1", "category": "connector", "permissions": ["read:cohorts", "write:cohorts"]}
ALL = [
    {"id": "a1", "category": "connector", "permissions": ["read:cohorts"]},
    {"id": "a2", "category": "connector", "permissions": ["read:cohorts"], "install_count": 100},
    {"id": "a3", "category": "automation", "permissions": ["subscribe:events"], "install_count": 50},
    {"id": "a4", "category": "analytics", "permissions": [], "install_count": 10},
]

def test_same_category_first():
    r = find_related(app=APP, all_apps=ALL)
    assert r[0]["id"] == "a2"

def test_excludes_self():
    r = find_related(app=APP, all_apps=ALL)
    assert all(a["id"] != "a1" for a in r)

def test_limit():
    r = find_related(app=APP, all_apps=ALL, limit=1)
    assert len(r) <= 1

def test_empty():
    assert find_related(app=APP, all_apps=[]) == []
