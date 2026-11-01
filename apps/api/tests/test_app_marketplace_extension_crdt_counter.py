from app.services.app_marketplace_extension_crdt_counter import (
    GCounter, PNCounter, CrdtCounterService
)


def test_g_counter_increment():
    gc = GCounter("A")
    gc.increment(5)
    gc.increment(3)
    assert gc.value == 8


def test_g_counter_no_decrement():
    gc = GCounter("A")
    try:
        gc.increment(-1)
        assert False
    except ValueError:
        pass


def test_g_counter_merge():
    a = GCounter("A")
    b = GCounter("B")
    a.increment(3)
    b.increment(5)
    merged = a.merge(b)
    assert merged.value == 8  # 3 from A + 5 from B


def test_g_counter_merge_idempotent():
    a = GCounter("A")
    a.increment(3)
    b = GCounter("B")
    b.increment(5)
    m1 = a.merge(b)
    m2 = m1.merge(b)  # merge again = same result
    assert m1.value == m2.value


def test_g_counter_merge_commutative():
    a = GCounter("A"); a.increment(3)
    b = GCounter("B"); b.increment(5)
    assert a.merge(b).value == b.merge(a).value


def test_pn_counter():
    pn = PNCounter("A")
    pn.increment(10)
    pn.decrement(3)
    assert pn.value == 7


def test_pn_counter_merge():
    a = PNCounter("A")
    b = PNCounter("B")
    a.increment(10)
    b.increment(5)
    a.decrement(2)
    b.decrement(1)
    merged = a.merge(b)
    assert merged.value == 12  # (10+5) - (2+1)


def test_service_distributed():
    svc = CrdtCounterService()
    svc.create_g_counter("page_views", ["node-1", "node-2", "node-3"])
    svc.g_increment("page_views", "node-1", 100)
    svc.g_increment("page_views", "node-2", 200)
    svc.g_increment("page_views", "node-3", 50)
    # Each node sees only its own count
    assert svc.get_g_value("page_views", "node-1") == 100
    # Sync merges all
    total = svc.sync_g("page_views")
    assert total == 350


def test_pn_service():
    svc = CrdtCounterService()
    svc.create_pn_counter("likes", ["A", "B"])
    svc.pn_increment("likes", "A", 10)
    svc.pn_increment("likes", "B", 5)
    svc.pn_decrement("likes", "A", 2)
    total = svc.sync_pn("likes")
    assert total == 13


def test_serialization():
    gc = GCounter("A")
    gc.increment(42)
    data = gc.to_dict()
    restored = GCounter.from_dict(data)
    assert restored.value == 42
