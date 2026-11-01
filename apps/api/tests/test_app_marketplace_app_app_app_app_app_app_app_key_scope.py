from app.services.app_marketplace_app_app_app_app_app_app_app_key_scope import KeyScopeManager
import hashlib

def test_create_check():
    ksm = KeyScopeManager()
    r = ksm.create_key("ci-key", ["read", "deploy"], "ci-system")
    key_hash = hashlib.sha256(r["key"].encode()).hexdigest()
    assert ksm.check_scope(key_hash, "read")["allowed"]
    assert ksm.check_scope(key_hash, "deploy")["allowed"]
    assert not ksm.check_scope(key_hash, "admin")["allowed"]

def test_wildcard():
    ksm = KeyScopeManager()
    r = ksm.create_key("admin-key", ["*"], "admin")
    key_hash = hashlib.sha256(r["key"].encode()).hexdigest()
    assert ksm.check_scope(key_hash, "anything")["allowed"]

def test_revoke():
    ksm = KeyScopeManager()
    r = ksm.create_key("temp", ["read"], "user")
    key_hash = hashlib.sha256(r["key"].encode()).hexdigest()
    ksm.revoke(key_hash)
    assert not ksm.check_scope(key_hash, "read")["allowed"]
