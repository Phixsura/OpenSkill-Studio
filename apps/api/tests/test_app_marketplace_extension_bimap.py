from app.services.app_marketplace_extension_bimap import BiMap, BiMapService


def test_forward_and_inverse():
    bm = BiMap()
    bm.put("user_123", "alice@example.com")
    assert bm.get_by_key("user_123") == "alice@example.com"
    assert bm.get_by_value("alice@example.com") == "user_123"


def test_bijection_enforced():
    bm = BiMap()
    bm.put("a", 1)
    bm.put("b", 1)  # value 1 reassigned from 'a' to 'b'
    assert bm.get_by_value(1) == "b"
    assert bm.get_by_key("a") is None  # 'a' removed (old mapping)


def test_update_key():
    bm = BiMap()
    bm.put("x", "old")
    bm.put("x", "new")  # update value for key 'x'
    assert bm.get_by_key("x") == "new"
    assert bm.get_by_value("old") is None  # old value cleaned up
    assert bm.get_by_value("new") == "x"


def test_remove_by_key():
    bm = BiMap()
    bm.put("k", "v")
    assert bm.remove_by_key("k") is True
    assert bm.contains_key("k") is False
    assert bm.contains_value("v") is False


def test_remove_by_value():
    bm = BiMap()
    bm.put("k", "v")
    assert bm.remove_by_value("v") is True
    assert bm.size == 0


def test_contains():
    bm = BiMap()
    bm.put(1, "one")
    assert bm.contains_key(1) is True
    assert bm.contains_value("one") is True
    assert bm.contains_key(2) is False


def test_from_dict():
    bm = BiMap.from_dict({"a": 1, "b": 2, "c": 3})
    assert bm.size == 3
    assert bm.get_by_value(2) == "b"


def test_iteration():
    bm = BiMap()
    bm.put("x", 1)
    bm.put("y", 2)
    assert set(bm.keys()) == {"x", "y"}
    assert set(bm.values()) == {1, 2}
    assert len(bm.items()) == 2
    assert len(bm.inverse_items()) == 2


def test_clear():
    bm = BiMap()
    bm.put("a", 1)
    bm.clear()
    assert bm.size == 0


def test_default_value():
    bm = BiMap()
    assert bm.get_by_key("missing", "default") == "default"
    assert bm.get_by_value("missing", -1) == -1


def test_service():
    svc = BiMapService()
    bm = svc.create("codes")
    bm.put(200, "OK")
    bm.put(404, "Not Found")
    retrieved = svc.get("codes")
    assert retrieved.get_by_value("OK") == 200
