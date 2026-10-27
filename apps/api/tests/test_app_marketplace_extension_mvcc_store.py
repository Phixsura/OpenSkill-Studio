from app.services.app_marketplace_extension_mvcc_store import MvccStoreService
import time


def test_read_write_commit():
    store = MvccStoreService()
    tx = store.begin()
    store.write(tx.tx_id, "user:1", {"name": "Alice"})
    assert store.read(tx.tx_id, "user:1") == {"name": "Alice"}  # read own writes
    store.commit(tx.tx_id)
    # New tx should see committed data
    tx2 = store.begin()
    assert store.read(tx2.tx_id, "user:1") == {"name": "Alice"}


def test_snapshot_isolation():
    store = MvccStoreService()
    # tx1 writes
    tx1 = store.begin()
    store.write(tx1.tx_id, "key", "v1")
    store.commit(tx1.tx_id)
    # tx2 starts (sees v1)
    tx2 = store.begin()
    # tx3 updates key after tx2's snapshot
    time.sleep(0.001)
    tx3 = store.begin()
    store.write(tx3.tx_id, "key", "v2")
    store.commit(tx3.tx_id)
    # tx2 should still see v1 (snapshot isolation)
    assert store.read(tx2.tx_id, "key") == "v1"


def test_write_write_conflict():
    store = MvccStoreService()
    tx1 = store.begin()
    store.write(tx1.tx_id, "shared", "from-tx1")
    time.sleep(0.001)
    tx2 = store.begin()
    store.write(tx2.tx_id, "shared", "from-tx2")
    # tx1 commits first
    assert store.commit(tx1.tx_id) is True
    # tx2 should fail (conflict: tx1 wrote after tx2's snapshot)
    assert store.commit(tx2.tx_id) is False


def test_delete():
    store = MvccStoreService()
    tx1 = store.begin()
    store.write(tx1.tx_id, "key", "value")
    store.commit(tx1.tx_id)
    tx2 = store.begin()
    store.delete(tx2.tx_id, "key")
    store.commit(tx2.tx_id)
    tx3 = store.begin()
    assert store.read(tx3.tx_id, "key") is None


def test_abort():
    store = MvccStoreService()
    tx = store.begin()
    store.write(tx.tx_id, "key", "value")
    store.abort(tx.tx_id)
    tx2 = store.begin()
    assert store.read(tx2.tx_id, "key") is None


def test_read_nonexistent():
    store = MvccStoreService()
    tx = store.begin()
    assert store.read(tx.tx_id, "nope") is None


def test_gc():
    store = MvccStoreService()
    for i in range(5):
        tx = store.begin()
        store.write(tx.tx_id, "key", f"v{i}")
        store.commit(tx.tx_id)
        time.sleep(0.001)
    assert store.get_version_count("key") == 5
    removed = store.gc(keep_versions=2)
    assert removed == 3
    assert store.get_version_count("key") == 2


def test_multiple_keys():
    store = MvccStoreService()
    tx = store.begin()
    store.write(tx.tx_id, "a", 1)
    store.write(tx.tx_id, "b", 2)
    store.write(tx.tx_id, "c", 3)
    store.commit(tx.tx_id)
    tx2 = store.begin()
    assert store.read(tx2.tx_id, "a") == 1
    assert store.read(tx2.tx_id, "b") == 2
    assert store.read(tx2.tx_id, "c") == 3
