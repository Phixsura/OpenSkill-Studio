from app.services.app_marketplace_extension_capped_collection import CappedCollectionService


def test_insert_and_find():
    cc = CappedCollectionService(max_docs=100)
    cc.insert({"name": "Alice"})
    cc.insert({"name": "Bob"})
    docs = cc.find()
    assert len(docs) == 2
    assert docs[0].data["name"] == "Alice"  # FIFO order


def test_cap_eviction():
    cc = CappedCollectionService(max_docs=3)
    cc.insert({"i": 1})
    cc.insert({"i": 2})
    cc.insert({"i": 3})
    cc.insert({"i": 4})  # evicts i:1
    assert cc.count() == 3
    docs = cc.find()
    assert docs[0].data["i"] == 2  # oldest remaining


def test_byte_cap():
    cc = CappedCollectionService(max_docs=10000, max_bytes=100)
    for i in range(50):
        cc.insert({"value": "x" * 10})
    # Should have evicted to stay under 100 bytes
    assert cc.stats()["current_bytes"] <= 100


def test_find_latest():
    cc = CappedCollectionService(max_docs=100)
    for i in range(10):
        cc.insert({"i": i})
    latest = cc.find_latest(3)
    assert latest[0].data["i"] == 9  # most recent first
    assert latest[2].data["i"] == 7


def test_tailable_cursor():
    cc = CappedCollectionService(max_docs=100)
    cc.insert({"i": 1})
    cc.insert({"i": 2})
    # First read
    batch1 = cc.tail("cursor-1", batch_size=10)
    assert len(batch1) == 2
    # Insert more
    cc.insert({"i": 3})
    # Second read picks up only new
    batch2 = cc.tail("cursor-1", batch_size=10)
    assert len(batch2) == 1
    assert batch2[0].data["i"] == 3


def test_bulk_insert():
    cc = CappedCollectionService(max_docs=100)
    count = cc.insert_many([{"i": i} for i in range(5)])
    assert count == 5
    assert cc.count() == 5


def test_stats():
    cc = CappedCollectionService(max_docs=5)
    for i in range(8):
        cc.insert({"i": i})
    stats = cc.stats()
    assert stats["count"] == 5
    assert stats["total_inserted"] == 8
    assert stats["total_evicted"] == 3
    assert stats["utilization_pct"] == 100.0


def test_empty():
    cc = CappedCollectionService()
    assert cc.count() == 0
    assert cc.find() == []
    assert cc.find_latest() == []


def test_skip():
    cc = CappedCollectionService()
    for i in range(10):
        cc.insert({"i": i})
    docs = cc.find(limit=3, skip=5)
    assert len(docs) == 3
    assert docs[0].data["i"] == 5
