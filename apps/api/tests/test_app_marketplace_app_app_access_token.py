from app.services.app_marketplace_app_app_access_token import generate_access_token, verify_token_signature, check_scope

def test_generate():
    r = generate_access_token(user_id="u1", scopes=["read", "write"], ttl_minutes=30)
    assert len(r["token"]) > 20
    assert r["ttl_minutes"] == 30
    assert r["scopes"] == ["read", "write"]

def test_verify():
    r = generate_access_token(user_id="u1", scopes=[])
    assert verify_token_signature(token=r["token"], signature=r["signature"])
    assert not verify_token_signature(token=r["token"], signature="bad_0000000000")

def test_scope_allowed():
    assert check_scope(required="read", granted=["read", "write"])["allowed"]
    assert check_scope(required="delete", granted=["admin"])["allowed"]
    assert check_scope(required="anything", granted=["*"])["allowed"]

def test_scope_denied():
    assert not check_scope(required="delete", granted=["read"])["allowed"]
