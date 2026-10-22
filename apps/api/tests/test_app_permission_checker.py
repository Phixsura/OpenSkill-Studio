from app.services.app_permission_checker import check_operation, check_bulk_operations

def test_allowed():
    r = check_operation(granted_scopes=["read:cohorts"], required_scope="read:cohorts")
    assert r["allowed"] is True

def test_denied():
    r = check_operation(granted_scopes=[], required_scope="read:cohorts")
    assert r["allowed"] is False

def test_unknown_scope():
    r = check_operation(granted_scopes=["admin:all"], required_scope="admin:all")
    assert r["allowed"] is False

def test_bulk_all_allowed():
    ops = [{"name": "list cohorts", "scope": "read:cohorts"}, {"name": "list projects", "scope": "read:projects"}]
    r = check_bulk_operations(granted_scopes=["read:cohorts", "read:projects"], operations=ops)
    assert r["all_allowed"] is True

def test_bulk_some_denied():
    ops = [{"name": "read", "scope": "read:cohorts"}, {"name": "write", "scope": "write:cohorts"}]
    r = check_bulk_operations(granted_scopes=["read:cohorts"], operations=ops)
    assert r["all_allowed"] is False
    assert r["denied"] == 1
