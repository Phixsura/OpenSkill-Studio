from app.services.app_marketplace_app_token_scoping import expand_scopes, check_scope, create_scoped_token

def test_expand_admin():
    e = expand_scopes(scopes=["admin"])
    assert "read" in e
    assert "write" in e
    assert "delete" in e

def test_expand_write():
    e = expand_scopes(scopes=["write"])
    assert "read" in e
    assert "admin" not in e

def test_check_ok():
    assert check_scope(token_scopes=["admin"], required_scope="read")

def test_check_fail():
    assert not check_scope(token_scopes=["read"], required_scope="write")

def test_create():
    t = create_scoped_token(app_id="a1", scopes=["write"], name="ci-token")
    assert "read" in t["effective_scopes"]
    assert "write" in t["effective_scopes"]

def test_invalid_scope():
    t = create_scoped_token(app_id="a1", scopes=["superpower"], name="x")
    assert t["error"]
