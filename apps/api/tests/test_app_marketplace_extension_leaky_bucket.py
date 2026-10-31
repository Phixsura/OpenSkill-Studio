from app.services.app_marketplace_extension_leaky_bucket import LeakyBucketService
import time


def test_accept_request():
    svc = LeakyBucketService()
    svc.configure("api", drain_rate=10, max_queue=5)
    result = svc.submit("api", "req-1")
    assert result["accepted"] is True
    assert result["queue_position"] == 1


def test_reject_when_full():
    svc = LeakyBucketService()
    svc.configure("api", drain_rate=0.001, max_queue=3)  # very slow drain
    svc.submit("api")
    svc.submit("api")
    svc.submit("api")
    result = svc.submit("api")
    assert result["accepted"] is False
    assert result["queue_depth"] == 3


def test_drain_frees_space():
    svc = LeakyBucketService()
    svc.configure("api", drain_rate=1000, max_queue=3)
    svc.submit("api")
    svc.submit("api")
    svc.submit("api")
    time.sleep(0.01)
    # After draining, should accept again
    result = svc.submit("api")
    assert result["accepted"] is True


def test_manual_drain():
    svc = LeakyBucketService()
    svc.configure("api", drain_rate=0.001, max_queue=10)
    svc.submit("api", "req-1")
    svc.submit("api", "req-2")
    item = svc.drain_one("api")
    assert item["id"] == "req-1"  # FIFO
    item2 = svc.drain_one("api")
    assert item2["id"] == "req-2"
    assert svc.drain_one("api") is None  # empty


def test_estimated_wait():
    svc = LeakyBucketService()
    svc.configure("api", drain_rate=10, max_queue=100)  # 10/sec
    for i in range(5):
        svc.submit("api")
    result = svc.submit("api")
    # 6 items in queue at 10/sec = 600ms estimated wait
    assert result["estimated_wait_ms"] >= 500


def test_independent_buckets():
    svc = LeakyBucketService()
    svc.configure("fast", drain_rate=100, max_queue=10)
    svc.configure("slow", drain_rate=0.001, max_queue=2)
    svc.submit("slow")
    svc.submit("slow")
    assert svc.submit("slow")["accepted"] is False
    assert svc.submit("fast")["accepted"] is True


def test_stats():
    svc = LeakyBucketService()
    svc.configure("api", drain_rate=1000, max_queue=10)
    svc.submit("api")
    svc.submit("api")
    stats = svc.stats("api")
    assert stats["total_accepted"] == 2
    assert stats["drain_rate"] == 1000
    assert stats["utilization"] >= 0


def test_queue_depth_after_time():
    svc = LeakyBucketService()
    svc.configure("api", drain_rate=1000, max_queue=100)
    for _ in range(10):
        svc.submit("api")
    time.sleep(0.02)
    depth = svc.get_queue_depth("api")
    assert depth < 10  # some should have drained
