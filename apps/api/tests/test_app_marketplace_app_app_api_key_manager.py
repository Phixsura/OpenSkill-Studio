from app.services.app_marketplace_app_app_api_key_manager import create_api_key, list_api_keys, revoke_api_key

def test_create():
    r = create_api_key(name="My Key", scopes=["read", "write"])
    assert r["key"].startswith("osk_")
    assert len(r["key"]) == 52  # "osk_" + 48 hex chars
    assert r["scopes"] == ["read", "write"]

def test_list():
    keys = [{"prefix": "osk_abcd", "name": "K1", "scopes": ["read"], "revoked": False},
            {"prefix": "osk_efgh", "name": "K2", "scopes": [], "revoked": True}]
    r = list_api_keys(keys=keys)
    assert r["total"] == 2
    assert r["active"] == 1

def test_revoke():
    keys = [{"prefix": "osk_abcd", "revoked": False}]
    r = revoke_api_key(keys=keys, prefix="osk_abcd")
    assert r["revoked"]
    assert keys[0]["revoked"]
