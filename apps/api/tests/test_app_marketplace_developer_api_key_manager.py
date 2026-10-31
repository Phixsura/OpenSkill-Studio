from app.services.app_marketplace_developer_api_key_manager import (
    create_api_key, revoke_api_key, list_api_keys)

def test_create():
    r = create_api_key(developer_id="d1", label="Prod", scopes=["read", "write"])
    assert r["success"]
    assert len(r["key"]) > 20
    assert r["key_prefix"] == r["key"][:8]
    assert "warning" in r

def test_invalid_scope():
    r = create_api_key(developer_id="d1", label="X", scopes=["delete_all"])
    assert not r["success"]
    assert "Invalid scopes" in r["error"]

def test_revoke():
    r = revoke_api_key(key_prefix="sk_abc1")
    assert r["success"]

def test_list():
    r = list_api_keys(developer_id="d1")
    assert r["total"] == 2
    assert r["keys"][0]["status"] == "active"
