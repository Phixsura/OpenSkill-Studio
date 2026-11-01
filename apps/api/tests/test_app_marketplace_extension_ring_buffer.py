from app.services.app_marketplace_extension_ring_buffer import RingBufferService


def test_write_and_read():
    rb = RingBufferService(capacity=10)
    rb.write("event-1")
    rb.write("event-2")
    entries = rb.read("consumer-a", count=2)
    assert len(entries) == 2
    assert entries[0].data == "event-1"
    assert entries[1].data == "event-2"


def test_consumer_position():
    rb = RingBufferService(capacity=10)
    for i in range(5):
        rb.write(f"e{i}")
    # Consumer reads 3, then 2 more
    batch1 = rb.read("c1", count=3)
    assert len(batch1) == 3
    batch2 = rb.read("c1", count=10)
    assert len(batch2) == 2  # only 2 remaining


def test_independent_consumers():
    rb = RingBufferService(capacity=10)
    for i in range(5):
        rb.write(i)
    c1 = rb.read("consumer-1", count=3)
    c2 = rb.read("consumer-2", count=5)
    assert len(c1) == 3
    assert len(c2) == 5  # independent position


def test_overwrite_on_full():
    rb = RingBufferService(capacity=3, overwrite=True)
    rb.write("a")
    rb.write("b")
    rb.write("c")
    rb.write("d")  # overwrites "a"
    # New consumer starts from oldest available
    entries = rb.read("c1", count=10)
    assert len(entries) == 3
    assert entries[0].data == "b"  # "a" was overwritten


def test_reject_on_full():
    rb = RingBufferService(capacity=3, overwrite=False)
    rb.write("a")
    rb.write("b")
    rb.write("c")
    try:
        rb.write("d")
        assert False
    except BufferError:
        pass


def test_peek_does_not_advance():
    rb = RingBufferService(capacity=10)
    rb.write("x")
    peeked = rb.peek("c1", count=1)
    assert len(peeked) == 1
    # Read again — should get same data
    read = rb.read("c1", count=1)
    assert read[0].data == peeked[0].data


def test_batch_write():
    rb = RingBufferService(capacity=100)
    seqs = rb.write_batch(["a", "b", "c"])
    assert len(seqs) == 3
    assert seqs[0] < seqs[1] < seqs[2]


def test_backpressure():
    rb = RingBufferService(capacity=10)
    assert rb.backpressure_status() == "ok"
    for i in range(9):
        rb.write(i)
    assert rb.backpressure_status() == "critical"


def test_consumer_lag():
    rb = RingBufferService(capacity=100)
    for i in range(50):
        rb.write(i)
    rb.read("fast", count=45)
    rb.read("slow", count=10)
    stats = rb.stats()
    assert stats["consumer_lag"]["fast"] == 5
    assert stats["consumer_lag"]["slow"] == 40
