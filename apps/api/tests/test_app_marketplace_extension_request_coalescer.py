from app.services.app_marketplace_extension_request_coalescer import RequestCoalescerService


def test_single_execution():
    rc = RequestCoalescerService()
    call_count = [0]
    def expensive(params):
        call_count[0] += 1
        return {"data": params["id"]}
    result = rc.execute("get_user", {"id": 1}, expensive)
    assert result.result == {"data": 1}
    assert call_count[0] == 1


def test_cache_serves_second_call():
    rc = RequestCoalescerService()
    call_count = [0]
    def expensive(params):
        call_count[0] += 1
        return {"value": 42}
    rc.execute("fetch", {"key": "x"}, expensive, cache_ttl=60)
    result2 = rc.execute("fetch", {"key": "x"}, expensive, cache_ttl=60)
    assert call_count[0] == 1  # only called once
    assert result2.from_cache is True


def test_different_params_not_coalesced():
    rc = RequestCoalescerService()
    call_count = [0]
    def fn(params):
        call_count[0] += 1
        return params
    rc.execute("op", {"a": 1}, fn, cache_ttl=60)
    rc.execute("op", {"a": 2}, fn, cache_ttl=60)
    assert call_count[0] == 2  # different params = different executions


def test_cache_ttl_expiry():
    rc = RequestCoalescerService()
    call_count = [0]
    def fn(params):
        call_count[0] += 1
        return "result"
    rc.execute("op", {}, fn, cache_ttl=0.01)
    import time; time.sleep(0.02)
    rc.execute("op", {}, fn, cache_ttl=0.01)
    assert call_count[0] == 2  # cache expired, re-executed


def test_invalidate():
    rc = RequestCoalescerService()
    rc.execute("op", {"k": 1}, lambda p: "v1", cache_ttl=60)
    rc.invalidate("op", {"k": 1})
    call_count = [0]
    def fn(p):
        call_count[0] += 1
        return "v2"
    rc.execute("op", {"k": 1}, fn, cache_ttl=60)
    assert call_count[0] == 1  # had to re-execute after invalidation


def test_batch_execute():
    rc = RequestCoalescerService()
    results = rc.batch_execute([
        ("get", {"id": 1}, lambda p: {"id": p["id"]}),
        ("get", {"id": 2}, lambda p: {"id": p["id"]}),
        ("get", {"id": 1}, lambda p: {"id": p["id"]}),
    ], cache_ttl=60)
    assert len(results) == 3
    # Third call (same as first) should be coalesced
    assert rc.stats()["total_coalesced"] >= 1


def test_stats():
    rc = RequestCoalescerService()
    rc.execute("a", {}, lambda p: 1, cache_ttl=60)
    rc.execute("a", {}, lambda p: 1, cache_ttl=60)  # cached
    rc.execute("b", {}, lambda p: 2)
    stats = rc.stats()
    assert stats["total_calls"] == 3
    assert stats["total_executed"] == 2
    assert stats["total_coalesced"] == 1
    assert stats["savings_pct"] > 0


def test_no_cache():
    rc = RequestCoalescerService()
    call_count = [0]
    def fn(p):
        call_count[0] += 1
        return "x"
    rc.execute("op", {}, fn)  # no cache_ttl
    rc.execute("op", {}, fn)  # no cache_ttl
    assert call_count[0] == 2  # each call executes


def test_error_cleans_inflight():
    rc = RequestCoalescerService()
    try:
        rc.execute("fail", {}, lambda p: (_ for _ in ()).throw(RuntimeError("err")))
    except RuntimeError:
        pass
    assert rc.stats()["inflight"] == 0  # cleaned up
