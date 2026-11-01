from app.services.app_marketplace_extension_rate_shaper import RateShaperService


def test_submit():
    rs = RateShaperService(burst_capacity=10, drain_rate=5)
    result = rs.submit("r1")
    assert result["accepted"] is True
    assert result["queue"] == "normal"


def test_reject_when_full():
    rs = RateShaperService(burst_capacity=3, drain_rate=0.001)
    rs.submit("r1"); rs.submit("r2"); rs.submit("r3")
    result = rs.submit("r4")
    assert result["accepted"] is False
    assert result["reason"] == "queue full"


def test_priority_bypass():
    rs = RateShaperService(burst_capacity=2, drain_rate=0.001)
    rs.submit("r1"); rs.submit("r2")  # fill normal queue
    result = rs.submit("r3", priority="high")
    assert result["accepted"] is True  # priority bypasses capacity check


def test_drain_priority_first():
    rs = RateShaperService(burst_capacity=10, drain_rate=100)
    rs.submit("normal-1")
    rs.submit("high-1", priority="high")
    rs.submit("normal-2")
    drained = rs.drain(max_count=2)
    assert drained[0].request_id == "high-1"  # priority first


def test_drain_rate():
    rs = RateShaperService(burst_capacity=100, drain_rate=1000)
    for i in range(10):
        rs.submit(f"r{i}")
    import time; time.sleep(0.02)
    drained = rs.drain()
    assert len(drained) > 0  # should drain some based on elapsed time


def test_adjust_rate():
    rs = RateShaperService(drain_rate=10)
    new_rate = rs.adjust_rate(2.0)
    assert new_rate == 20.0
    new_rate = rs.adjust_rate(0.5)
    assert new_rate == 10.0


def test_backpressure():
    rs = RateShaperService(burst_capacity=10, drain_rate=0.001)
    assert rs.backpressure_status() == "ok"
    for i in range(9):
        rs.submit(f"r{i}")
    assert rs.backpressure_status() == "critical"


def test_stats():
    rs = RateShaperService(burst_capacity=20, drain_rate=10)
    rs.submit("a"); rs.submit("b")
    rs.submit("c", priority="high")
    stats = rs.stats()
    assert stats["queue_depth"] == 3
    assert stats["priority_queue"] == 1
    assert stats["total_accepted"] == 3


def test_estimated_wait():
    rs = RateShaperService(burst_capacity=100, drain_rate=10)
    for i in range(5):
        rs.submit(f"r{i}")
    result = rs.submit("r5")
    assert result["estimated_wait_ms"] > 0
