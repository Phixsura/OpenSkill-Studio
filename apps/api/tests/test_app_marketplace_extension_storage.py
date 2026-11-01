from app.services.app_marketplace_extension_storage import ExtensionStorage


def test_put_get_delete():
    s = ExtensionStorage()
    ok, _ = s.put("ext-1", "org-1", "config", {"theme": "dark"})
    assert ok
    assert s.get("ext-1", "org-1", "config") == {"theme": "dark"}
    assert s.delete("ext-1", "org-1", "config") is True
    assert s.get("ext-1", "org-1", "config") is None


def test_isolation():
    s = ExtensionStorage()
    s.put("ext-1", "org-a", "key", "value-a")
    s.put("ext-1", "org-b", "key", "value-b")
    assert s.get("ext-1", "org-a", "key") == "value-a"
    assert s.get("ext-1", "org-b", "key") == "value-b"


def test_namespaces():
    s = ExtensionStorage()
    s.put("ext-2", "org-1", "count", 10, ns="analytics")
    s.put("ext-2", "org-1", "count", 99, ns="cache")
    assert s.get("ext-2", "org-1", "count", ns="analytics") == 10
    assert s.get("ext-2", "org-1", "count", ns="cache") == 99


def test_ttl():
    s = ExtensionStorage()
    s.put("ext-3", "org-1", "temp", "gone", ttl_seconds=-1)
    assert s.get("ext-3", "org-1", "temp") is None


def test_increment():
    s = ExtensionStorage()
    assert s.increment("ext-4", "org-1", "views") == 1
    assert s.increment("ext-4", "org-1", "views") == 2
    assert s.increment("ext-4", "org-1", "views", 10) == 12


def test_list_operations():
    s = ExtensionStorage()
    s.list_push("ext-5", "org-1", "log", "event-1")
    s.list_push("ext-5", "org-1", "log", "event-2")
    s.list_push("ext-5", "org-1", "log", "event-3")
    items = s.list_get("ext-5", "org-1", "log")
    assert items == ["event-1", "event-2", "event-3"]


def test_keys_with_prefix():
    s = ExtensionStorage()
    s.put("ext-6", "org-1", "user:1", "alice")
    s.put("ext-6", "org-1", "user:2", "bob")
    s.put("ext-6", "org-1", "config", "val")
    user_keys = s.keys("ext-6", "org-1", prefix="user:")
    assert user_keys == ["user:1", "user:2"]


def test_clear():
    s = ExtensionStorage()
    s.put("ext-7", "org-1", "a", 1)
    s.put("ext-7", "org-1", "b", 2)
    count = s.clear("ext-7", "org-1")
    assert count == 2
    assert s.keys("ext-7", "org-1") == []
