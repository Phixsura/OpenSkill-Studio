from app.services.app_marketplace_app_app_app_app_app_app_app_dist_counter import DistributedCounter

def test_counter():
    dc = DistributedCounter(shards=4)
    dc.increment(shard=0, amount=10)
    dc.increment(shard=1, amount=20)
    dc.increment(shard=2, amount=30)
    assert dc.total() == 60
    dc.decrement(shard=0, amount=5)
    assert dc.total() == 55
    s = dc.stats()
    assert s["shards"] == 4
    assert s["shard_values"][0] == 5
