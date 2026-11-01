from app.services.app_marketplace_extension_consistent_hash import ConsistentHashRingService


def test_add_node():
    ring = ConsistentHashRingService(virtual_nodes=10)
    vnodes = ring.add_node("node-1", "host1:8080")
    assert vnodes == 10
    assert ring.stats()["physical_nodes"] == 1
    assert ring.stats()["virtual_nodes"] == 10


def test_basic_routing():
    ring = ConsistentHashRingService(virtual_nodes=50)
    ring.add_node("node-1", "h1:8080")
    ring.add_node("node-2", "h2:8080")
    node = ring.get_node("my-key")
    assert node in ("node-1", "node-2")


def test_deterministic():
    ring = ConsistentHashRingService(virtual_nodes=50)
    ring.add_node("a", "ha")
    ring.add_node("b", "hb")
    # Same key always maps to same node
    results = {ring.get_node("test-key-123") for _ in range(100)}
    assert len(results) == 1


def test_minimal_rehashing():
    ring = ConsistentHashRingService(virtual_nodes=100)
    ring.add_node("node-1", "h1")
    ring.add_node("node-2", "h2")

    keys = [f"key-{i}" for i in range(1000)]
    before = {k: ring.get_node(k) for k in keys}

    ring.add_node("node-3", "h3")
    after = {k: ring.get_node(k) for k in keys}

    # Only ~1/3 of keys should move (K/N ≈ 1000/3 ≈ 333)
    moved = sum(1 for k in keys if before[k] != after[k])
    assert moved < 500  # generous bound, expect ~333


def test_weighted_node():
    ring = ConsistentHashRingService(virtual_nodes=50)
    ring.add_node("heavy", "h1", weight=3)
    ring.add_node("light", "h2", weight=1)
    # Heavy node should get ~3x the virtual nodes
    assert ring.stats()["virtual_nodes"] == 200  # 50*3 + 50*1

    keys = [f"k-{i}" for i in range(1000)]
    dist = ring.get_distribution(keys)
    # Heavy should get roughly 3x traffic
    ratio = dist["heavy"] / max(1, dist["light"])
    assert 1.5 < ratio < 5  # roughly 3x, with some variance


def test_replication():
    ring = ConsistentHashRingService(virtual_nodes=50)
    ring.add_node("a", "ha")
    ring.add_node("b", "hb")
    ring.add_node("c", "hc")
    nodes = ring.get_nodes("my-data", count=2)
    assert len(nodes) == 2
    assert len(set(nodes)) == 2  # unique physical nodes


def test_replication_cap():
    ring = ConsistentHashRingService(virtual_nodes=50)
    ring.add_node("a", "ha")
    ring.add_node("b", "hb")
    # Request 5 replicas but only 2 nodes exist
    nodes = ring.get_nodes("key", count=5)
    assert len(nodes) == 2


def test_remove_node():
    ring = ConsistentHashRingService(virtual_nodes=50)
    ring.add_node("node-1", "h1")
    ring.add_node("node-2", "h2")
    ring.remove_node("node-1")
    # All keys should now go to node-2
    for i in range(20):
        assert ring.get_node(f"key-{i}") == "node-2"


def test_empty_ring():
    ring = ConsistentHashRingService()
    assert ring.get_node("key") is None
    assert ring.get_nodes("key") == []


def test_duplicate_node_rejected():
    ring = ConsistentHashRingService(virtual_nodes=10)
    ring.add_node("a", "ha")
    try:
        ring.add_node("a", "ha2")
        assert False
    except ValueError:
        pass
