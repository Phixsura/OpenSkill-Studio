from app.services.app_marketplace_token_introspection import introspect_token, check_token_scope, compute_token_usage_stats

def test_active():
    tokens = {"hash1": {"app_id": "a1", "scopes": ["read"], "issued_at": 1000, "expires_at": 0}}
    r = introspect_token(token_hash="hash1", stored_tokens=tokens)
    assert r["active"]
    assert r["scopes"] == ["read"]

def test_not_found():
    r = introspect_token(token_hash="missing", stored_tokens={})
    assert not r["active"]

def test_revoked():
    tokens = {"hash1": {"revoked": True, "scopes": []}}
    r = introspect_token(token_hash="hash1", stored_tokens=tokens)
    assert not r["active"]

def test_scope_ok():
    r = check_token_scope(token_scopes=["read", "write"], required_scope="read")
    assert r["authorized"]

def test_scope_admin():
    r = check_token_scope(token_scopes=["admin"], required_scope="anything")
    assert r["authorized"]

def test_scope_missing():
    r = check_token_scope(token_scopes=["read"], required_scope="write")
    assert not r["authorized"]

def test_stats():
    tokens = [{"active": True}, {"expired": True}, {"revoked": True}, {"active": True}]
    s = compute_token_usage_stats(tokens=tokens)
    assert s["active"] == 2
    assert s["expired"] == 1
