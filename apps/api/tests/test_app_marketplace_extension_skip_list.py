from app.services.app_marketplace_extension_skip_list import SkipListService
import random


def test_insert_and_search():
    sl = SkipListService()
    sl.insert(10, "ten")
    sl.insert(5, "five")
    sl.insert(15, "fifteen")
    assert sl.search(10) == "ten"
    assert sl.search(5) == "five"
    assert sl.search(99) is None


def test_update():
    sl = SkipListService()
    sl.insert("key", "v1")
    sl.insert("key", "v2")
    assert sl.search("key") == "v2"
    assert sl.size == 1


def test_delete():
    sl = SkipListService()
    sl.insert(1, "a")
    sl.insert(2, "b")
    sl.insert(3, "c")
    assert sl.delete(2) is True
    assert sl.search(2) is None
    assert sl.size == 2
    assert sl.delete(99) is False


def test_sorted_order():
    sl = SkipListService()
    random.seed(42)
    values = list(range(50))
    random.shuffle(values)
    for v in values:
        sl.insert(v, f"val-{v}")
    result = sl.to_sorted_list()
    keys = [k for k, _ in result]
    assert keys == list(range(50))


def test_range_query():
    sl = SkipListService()
    for i in range(1, 21):
        sl.insert(i, f"v{i}")
    result = sl.range_query(5, 10)
    keys = [k for k, _ in result]
    assert keys == [5, 6, 7, 8, 9, 10]


def test_empty():
    sl = SkipListService()
    assert sl.search("x") is None
    assert sl.size == 0
    assert sl.to_sorted_list() == []
    assert sl.range_query(0, 100) == []


def test_many_operations():
    sl = SkipListService()
    random.seed(123)
    for i in range(200):
        sl.insert(i, i * 10)
    assert sl.size == 200
    # Delete half
    for i in range(0, 200, 2):
        sl.delete(i)
    assert sl.size == 100
    # Verify remaining
    for i in range(200):
        if i % 2 == 0:
            assert sl.search(i) is None
        else:
            assert sl.search(i) == i * 10


def test_level_grows():
    sl = SkipListService(p=0.5)
    random.seed(42)
    for i in range(100):
        sl.insert(i, i)
    assert sl.level > 0  # should have multiple levels
