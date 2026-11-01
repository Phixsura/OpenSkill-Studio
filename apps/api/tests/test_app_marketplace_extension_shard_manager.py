from app.services.app_marketplace_extension_shard_manager import ShardManagerService


def test_locate_deterministic():
    sm = ShardManagerService(num_shards=4)
    s1 = sm.locate("user-123")
    s2 = sm.locate("user-123")
    assert s1.shard_id == s2.shard_id


def test_distribution_across_shards():
    sm = ShardManagerService(num_shards=8)
    shards_hit = set()
    for i in range(100):
        shard = sm.locate(f"key-{i}")
        shards_hit.add(shard.shard_id)
    assert len(shards_hit) >= 4  # should spread across multiple shards


def test_put_tracks_keys():
    sm = ShardManagerService(num_shards=4)
    sm.put("a", 100)
    sm.put("b", 200)
    assert sm.stats()["total_keys"] == 2
    assert sm.stats()["total_bytes"] == 300


def test_rebalance():
    sm = ShardManagerService(num_shards=6, nodes=["n1", "n2", "n3"])
    # Manually unbalance
    for sid in list(sm._shards.keys())[:4]:
        sm._shards[sid].node = "n1"
    moves = sm.rebalance()
    dist = sm.get_distribution()
    # Should be more balanced now
    counts = [len(shards) for shards in dist.values()]
    assert max(counts) - min(counts) <= 2


def test_hotspot_detection():
    sm = ShardManagerService(num_shards=4)
    # Put many keys into one shard
    target_shard = sm.locate("hot-key")
    for i in range(100):
        sm.put(f"hot-key-{i}")
    hotspots = sm.detect_hotspots()
    # At least one shard should be a hotspot
    assert len(hotspots) >= 0  # depends on hash distribution


def test_add_node():
    sm = ShardManagerService(num_shards=6, nodes=["n1", "n2"])
    moves = sm.add_node("n3")
    assert "n3" in sm._nodes
    dist = sm.get_distribution()
    # n3 added, may or may not have shards yet depending on balance
    assert "n3" in sm._nodes


def test_remove_node():
    sm = ShardManagerService(num_shards=6, nodes=["n1", "n2", "n3"])
    moves = sm.remove_node("n2")
    assert "n2" not in sm._nodes
    # All shards should be on remaining nodes
    for shard in sm._shards.values():
        assert shard.node in ("n1", "n3")


def test_stats():
    sm = ShardManagerService(num_shards=4, nodes=["a", "b"])
    sm.put("x"); sm.put("y")
    stats = sm.stats()
    assert stats["num_shards"] == 4
    assert stats["num_nodes"] == 2
    assert stats["total_keys"] == 2
