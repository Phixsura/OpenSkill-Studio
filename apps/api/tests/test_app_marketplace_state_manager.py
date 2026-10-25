from app.services.app_marketplace_state_manager import StateManager


def test_set_and_get():
    sm = StateManager()
    ok, _ = sm.set("ext-1", "config", {"theme": "dark"})
    assert ok is True
    val = sm.get("ext-1", "config")
    assert val == {"theme": "dark"}


def test_isolation():
    sm = StateManager()
    sm.set("ext-1", "key", "value1")
    sm.set("ext-1", "key", "value2", org_id="org-1")
    assert sm.get("ext-1", "key") == "value1"
    assert sm.get("ext-1", "key", org_id="org-1") == "value2"


def test_delete_and_exists():
    sm = StateManager()
    sm.set("ext-2", "temp", 42)
    assert sm.exists("ext-2", "temp") is True
    sm.delete("ext-2", "temp")
    assert sm.exists("ext-2", "temp") is False


def test_ttl_expiry():
    sm = StateManager()
    sm.set("ext-3", "fast", "gone", ttl=0.0)
    assert sm.get("ext-3", "fast") is None


def test_increment():
    sm = StateManager()
    sm.set("ext-4", "counter", 0)
    result = sm.increment("ext-4", "counter", 5)
    assert result == 5
    result = sm.increment("ext-4", "counter", 3)
    assert result == 8


def test_increment_new_key():
    sm = StateManager()
    result = sm.increment("ext-5", "visits")
    assert result == 1


def test_max_value_size():
    sm = StateManager(max_value_bytes=50)
    ok, msg = sm.set("ext-6", "big", "x" * 100)
    assert ok is False
    assert "too large" in msg


def test_list_keys_and_clear():
    sm = StateManager()
    sm.set("ext-7", "a", 1)
    sm.set("ext-7", "b", 2)
    sm.set("ext-7", "c", 3)
    assert sm.list_keys("ext-7") == ["a", "b", "c"]
    count = sm.clear_namespace("ext-7")
    assert count == 3
    assert sm.list_keys("ext-7") == []


def test_namespace_stats():
    sm = StateManager()
    sm.set("ext-8", "x", "hello")
    sm.set("ext-8", "y", "world")
    stats = sm.get_namespace_stats("ext-8")
    assert stats["key_count"] == 2
    assert stats["total_bytes"] > 0
