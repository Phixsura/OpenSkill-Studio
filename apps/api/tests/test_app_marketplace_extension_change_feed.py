from app.services.app_marketplace_extension_change_feed import ChangeFeedService


def test_append_and_read():
    cf = ChangeFeedService()
    cf.append("p1", "insert", "user-1", {"name": "Alice"})
    cf.append("p1", "insert", "user-2", {"name": "Bob"})
    changes = cf.read("consumer-1", "p1")
    assert len(changes) == 2
    assert changes[0].key == "user-1"


def test_checkpoint_resumes():
    cf = ChangeFeedService()
    cf.append("p1", "insert", "k1", {})
    cf.append("p1", "insert", "k2", {})
    cf.append("p1", "insert", "k3", {})
    batch1 = cf.read("c1", "p1", batch_size=2)
    cf.checkpoint("c1", "p1", batch1[-1].sequence)
    batch2 = cf.read("c1", "p1")
    assert len(batch2) == 1
    assert batch2[0].key == "k3"


def test_independent_consumers():
    cf = ChangeFeedService()
    cf.append("p1", "insert", "k1", {})
    cf.append("p1", "insert", "k2", {})
    c1 = cf.read("consumer-a", "p1")
    c2 = cf.read("consumer-b", "p1")
    assert len(c1) == 2
    assert len(c2) == 2  # independent


def test_partitions():
    cf = ChangeFeedService()
    cf.append("users", "insert", "u1", {})
    cf.append("orders", "insert", "o1", {})
    assert set(cf.get_partitions()) == {"users", "orders"}
    assert len(cf.read("c1", "users")) == 1
    assert len(cf.read("c1", "orders")) == 1


def test_process_batch():
    cf = ChangeFeedService()
    cf.append("p1", "insert", "k1", {"v": 1})
    cf.append("p1", "update", "k1", {"v": 2})
    processed = []
    result = cf.process_batch("c1", "p1",
                               lambda c: processed.append(c.data))
    assert result["processed"] == 2
    assert result["status"] == "ok"


def test_process_error_stops():
    cf = ChangeFeedService()
    cf.append("p1", "insert", "k1", {})
    cf.append("p1", "insert", "k2", {})
    cf.append("p1", "insert", "k3", {})
    count = [0]
    def fail_on_second(change):
        count[0] += 1
        if count[0] == 2:
            raise RuntimeError("fail")
    result = cf.process_batch("c1", "p1", fail_on_second)
    assert result["processed"] == 1  # only first succeeded
    assert result["status"] == "error"


def test_lag():
    cf = ChangeFeedService()
    for i in range(10):
        cf.append("p1", "insert", f"k{i}", {})
    assert cf.get_lag("c1", "p1") == 10
    batch = cf.read("c1", "p1", 3)
    cf.checkpoint("c1", "p1", batch[-1].sequence)
    assert cf.get_lag("c1", "p1") == 7


def test_consumer_status():
    cf = ChangeFeedService()
    cf.append("p1", "insert", "a", {})
    cf.append("p2", "insert", "b", {})
    cf.process_batch("c1", "p1", lambda c: None)
    status = cf.get_consumer_status("c1")
    assert status["partitions"]["p1"]["caught_up"] is True
    assert status["partitions"]["p2"]["caught_up"] is False


def test_caught_up():
    cf = ChangeFeedService()
    result = cf.process_batch("c1", "empty", lambda c: None)
    assert result["status"] == "caught_up"
