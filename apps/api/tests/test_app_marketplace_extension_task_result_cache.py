from app.services.app_marketplace_extension_task_result_cache import TaskResultCacheService
import time


def test_store_and_get():
    trc = TaskResultCacheService()
    trc.store("report", {"year": 2024}, {"total": 1000}, soft_ttl=60)
    result = trc.get("report", {"year": 2024})
    assert result["status"] == "fresh"
    assert result["result"]["total"] == 1000


def test_miss():
    trc = TaskResultCacheService()
    result = trc.get("missing", {})
    assert result["status"] == "miss"


def test_stale():
    trc = TaskResultCacheService()
    trc.store("report", {}, {"x": 1}, soft_ttl=0.01, hard_ttl=10)
    time.sleep(0.02)
    result = trc.get("report", {})
    assert result["status"] == "stale"
    assert result["result"]["x"] == 1  # still served


def test_expired():
    trc = TaskResultCacheService()
    trc.store("report", {}, {"x": 1}, soft_ttl=0.01, hard_ttl=0.01)
    time.sleep(0.02)
    result = trc.get("report", {})
    assert result["status"] == "expired"


def test_computation_lock():
    trc = TaskResultCacheService()
    assert trc.try_lock("heavy", {}) is True
    assert trc.try_lock("heavy", {}) is False  # already locked


def test_get_or_compute():
    trc = TaskResultCacheService()
    compute_count = [0]
    def compute(params):
        compute_count[0] += 1
        return {"value": params.get("x", 0) * 2}
    r1 = trc.get_or_compute("calc", {"x": 5}, compute, soft_ttl=60)
    assert r1["result"]["value"] == 10
    r2 = trc.get_or_compute("calc", {"x": 5}, compute, soft_ttl=60)
    assert r2["status"] == "fresh"
    assert compute_count[0] == 1  # computed only once


def test_different_params():
    trc = TaskResultCacheService()
    def compute(p):
        return {"sum": p["a"] + p["b"]}
    trc.get_or_compute("add", {"a": 1, "b": 2}, compute)
    trc.get_or_compute("add", {"a": 3, "b": 4}, compute)
    r1 = trc.get("add", {"a": 1, "b": 2})
    r2 = trc.get("add", {"a": 3, "b": 4})
    assert r1["result"]["sum"] == 3
    assert r2["result"]["sum"] == 7


def test_invalidate():
    trc = TaskResultCacheService()
    trc.store("report", {}, {"data": 1})
    assert trc.invalidate("report", {}) is True
    assert trc.get("report", {})["status"] == "miss"


def test_version_increments():
    trc = TaskResultCacheService()
    c1 = trc.store("r", {}, {"v": 1})
    c2 = trc.store("r", {}, {"v": 2})
    assert c2.version > c1.version
    assert c2.compute_count == 2


def test_stats():
    trc = TaskResultCacheService()
    trc.store("a", {}, {}, soft_ttl=60)
    trc.store("b", {}, {}, soft_ttl=0.001)
    time.sleep(0.002)
    stats = trc.stats()
    assert stats["total"] == 2
    assert stats["fresh"] >= 1
