from app.services.app_marketplace_extension_sandbox_kv_store import (
    SandboxKVStoreService,
)


def test_set_and_get():
    svc = SandboxKVStoreService()
    svc.set("sb-1", "name", "Alice")
    assert svc.get("sb-1", "name") == "Alice"


def test_get_missing():
    svc = SandboxKVStoreService()
    assert svc.get("sb-1", "nope") is None


def test_ttl_expiry():
    svc = SandboxKVStoreService()
    svc.set("sb-1", "temp", "value", ttl=-1)  # already expired
    assert svc.get("sb-1", "temp") is None


def test_delete():
    svc = SandboxKVStoreService()
    svc.set("sb-1", "key", "val")
    assert svc.delete("sb-1", "key") is True
    assert svc.get("sb-1", "key") is None


def test_increment():
    svc = SandboxKVStoreService()
    svc.set("sb-1", "counter", "10")
    result = svc.increment("sb-1", "counter", 5)
    assert result == 15
    assert svc.get("sb-1", "counter") == "15"


def test_increment_new_key():
    svc = SandboxKVStoreService()
    result = svc.increment("sb-1", "new_counter")
    assert result == 1


def test_append():
    svc = SandboxKVStoreService()
    svc.set("sb-1", "log", "line1\n")
    length = svc.append("sb-1", "log", "line2\n")
    assert length == 12
    assert svc.get("sb-1", "log") == "line1\nline2\n"


def test_scan():
    svc = SandboxKVStoreService()
    svc.set("sb-1", "user:1", "alice")
    svc.set("sb-1", "user:2", "bob")
    svc.set("sb-1", "config:theme", "dark")
    keys = svc.scan("sb-1", "user:")
    assert keys == ["user:1", "user:2"]


def test_count_and_clear():
    svc = SandboxKVStoreService()
    svc.set("sb-1", "a", "1")
    svc.set("sb-1", "b", "2")
    assert svc.count("sb-1") == 2
    assert svc.clear("sb-1") == 2
    assert svc.count("sb-1") == 0
