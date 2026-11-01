from app.services.app_marketplace_extension_btree_index import BTreeIndexService
import random


def test_insert_and_get():
    tree = BTreeIndexService(order=4)
    tree.insert(5, "five")
    tree.insert(3, "three")
    tree.insert(7, "seven")
    assert tree.get(5) == "five"
    assert tree.get(3) == "three"
    assert tree.get(99) is None


def test_ordered_iteration():
    tree = BTreeIndexService(order=4)
    for x in [50, 20, 70, 10, 30, 60, 80]:
        tree.insert(x, f"v{x}")
    result = tree.in_order()
    keys = [k for k, _ in result]
    assert keys == sorted(keys)


def test_range_query():
    tree = BTreeIndexService(order=4)
    for i in range(1, 21):
        tree.insert(i, f"val-{i}")
    result = tree.range_query(5, 10)
    keys = [k for k, _ in result]
    assert keys == [5, 6, 7, 8, 9, 10]


def test_min_max():
    tree = BTreeIndexService(order=4)
    for x in [30, 10, 50, 20, 40]:
        tree.insert(x, f"v{x}")
    assert tree.min_key() == (10, "v10")
    assert tree.max_key() == (50, "v50")


def test_update_existing_key():
    tree = BTreeIndexService(order=4)
    tree.insert("key", "v1")
    tree.insert("key", "v2")
    assert tree.get("key") == "v2"
    assert tree.size == 1


def test_many_inserts_with_splits():
    tree = BTreeIndexService(order=4)
    values = list(range(100))
    random.seed(42)
    random.shuffle(values)
    for v in values:
        tree.insert(v, f"val-{v}")
    assert tree.size == 100
    # All values retrievable
    for v in values:
        assert tree.get(v) == f"val-{v}"
    # Sorted order
    ordered = tree.in_order()
    keys = [k for k, _ in ordered]
    assert keys == list(range(100))


def test_string_keys():
    tree = BTreeIndexService(order=4)
    tree.insert("banana", 2)
    tree.insert("apple", 1)
    tree.insert("cherry", 3)
    tree.insert("date", 4)
    ordered = tree.in_order()
    keys = [k for k, _ in ordered]
    assert keys == ["apple", "banana", "cherry", "date"]


def test_empty_tree():
    tree = BTreeIndexService(order=4)
    assert tree.get("x") is None
    assert tree.min_key() is None
    assert tree.max_key() is None
    assert tree.range_query(1, 10) == []
    assert tree.in_order() == []
    assert tree.size == 0
