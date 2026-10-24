from app.services.app_marketplace_app_dependency_resolver import resolve_dependencies, check_version_compatibility

def test_resolve():
    available = {"auth": {"depends_on": []}, "db": {"depends_on": ["auth"]}}
    r = resolve_dependencies(app={"depends_on": ["db"]}, available=available)
    assert r["can_install"]
    assert r["install_order"] == ["auth", "db"]

def test_unresolved():
    r = resolve_dependencies(app={"depends_on": ["missing"]}, available={})
    assert not r["can_install"]
    assert "missing" in r["unresolved"]

def test_compatible():
    r = check_version_compatibility(required={"auth": "1.0"}, installed={"auth": "2.0"})
    assert r["compatible"]

def test_incompatible():
    r = check_version_compatibility(required={"auth": "2.0"}, installed={"auth": "1.0"})
    assert not r["compatible"]

def test_missing_dep():
    r = check_version_compatibility(required={"auth": "1.0"}, installed={})
    assert not r["compatible"]
    assert "auth" in r["missing"]
