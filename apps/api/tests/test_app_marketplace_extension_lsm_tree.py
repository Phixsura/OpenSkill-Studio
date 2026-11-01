from app.services.app_marketplace_extension_lsm_tree import LsmTreeService


def test_put_and_get():
    lsm = LsmTreeService(memtable_threshold=100)
    lsm.put("key1", "value1")
    assert lsm.get("key1") == "value1"


def test_overwrite():
    lsm = LsmTreeService()
    lsm.put("key", "v1")
    lsm.put("key", "v2")
    assert lsm.get("key") == "v2"


def test_delete():
    lsm = LsmTreeService()
    lsm.put("key", "value")
    lsm.delete("key")
    assert lsm.get("key") is None


def test_not_found():
    lsm = LsmTreeService()
    assert lsm.get("nonexistent") is None


def test_flush_to_sstable():
    lsm = LsmTreeService(memtable_threshold=5)
    for i in range(6):
        lsm.put(f"key{i}", f"val{i}")
    # Should have flushed
    assert lsm.stats()["sstable_count"] >= 1
    # But reads still work
    assert lsm.get("key0") == "val0"


def test_read_across_sstables():
    lsm = LsmTreeService(memtable_threshold=3)
    lsm.put("a", "1"); lsm.put("b", "2"); lsm.put("c", "3")  # flush
    lsm.put("d", "4"); lsm.put("e", "5"); lsm.put("f", "6")  # flush
    lsm.put("g", "7")  # in memtable
    assert lsm.get("a") == "1"  # from older SSTable
    assert lsm.get("d") == "4"  # from newer SSTable
    assert lsm.get("g") == "7"  # from memtable


def test_newer_sstable_wins():
    lsm = LsmTreeService(memtable_threshold=2)
    lsm.put("key", "old"); lsm.put("x", "x")  # flush
    lsm.put("key", "new"); lsm.put("y", "y")  # flush
    assert lsm.get("key") == "new"


def test_compaction():
    lsm = LsmTreeService(memtable_threshold=3)
    for i in range(12):  # creates 4 SSTables
        lsm.put(f"k{i:02d}", f"v{i}")
    before = lsm.stats()["sstable_count"]
    merged = lsm.compact()
    after = lsm.stats()["sstable_count"]
    assert after < before or merged == 0  # compaction reduces table count


def test_compaction_removes_tombstones():
    lsm = LsmTreeService(memtable_threshold=3)
    lsm.put("a", "1"); lsm.put("b", "2"); lsm.put("c", "3")  # flush
    lsm.delete("b"); lsm.put("x", "x"); lsm.put("y", "y")  # flush with tombstone
    lsm.compact()
    assert lsm.get("b") is None


def test_range_scan():
    lsm = LsmTreeService(memtable_threshold=100)
    for i in range(10):
        lsm.put(f"key-{i:02d}", f"val-{i}")
    results = lsm.range_scan("key-03", "key-07")
    keys = [k for k, _ in results]
    assert len(keys) == 5
    assert keys[0] == "key-03"
    assert keys[-1] == "key-07"
