from app.services.app_marketplace_app_app_app_app_app_app_app_api_key_mgr import (
    create_key, validate_key, revoke_key, list_keys, clear_keys,
)

def test_lifecycle():
    clear_keys()
    k = create_key("Test Key", ["read", "write"])
    assert k["key"].startswith("osk_")
    v = validate_key(k["key"])
    assert v["valid"]
    assert v["scopes"] == ["read", "write"]
    revoke_key(k["key"])
    v2 = validate_key(k["key"])
    assert not v2["valid"]
    assert v2["reason"] == "revoked"
    clear_keys()

def test_list():
    clear_keys()
    create_key("A", ["read"])
    create_key("B", ["write"])
    assert len(list_keys()) == 2
    clear_keys()
