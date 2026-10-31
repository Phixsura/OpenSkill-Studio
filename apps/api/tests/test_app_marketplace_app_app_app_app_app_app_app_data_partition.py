from app.services.app_marketplace_app_app_app_app_app_app_app_data_partition import DataPartitioner

def test_consistent():
    dp = DataPartitioner(num_shards=4)
    r1 = dp.partition("user-123")
    r2 = dp.partition("user-123")
    assert r1["shard"] == r2["shard"]

def test_batch():
    dp = DataPartitioner(num_shards=4)
    r = dp.batch_partition([f"key-{i}" for i in range(100)])
    assert r["total"] == 100
    assert sum(r["by_shard"].values()) == 100

def test_rebalance():
    dp = DataPartitioner(num_shards=2)
    for i in range(100):
        dp.partition(f"key-{i}")
    r = dp.rebalance_needed(threshold_pct=50)
    assert not r["needed"]  # hash should distribute reasonably
