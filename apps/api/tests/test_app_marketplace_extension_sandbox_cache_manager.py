from app.services.app_marketplace_extension_sandbox_cache_manager import (
    SandboxCacheManagerService,
)


def test_set_and_get():
    svc = SandboxCacheManagerService()
    svc.set("sb-1", "key1", "value1")
    assert svc.get("sb-1", "key1") == "value1"


def test_miss():
    svc = SandboxCacheManagerService()
    assert svc.get("sb-1", "missing") is None


def test_ttl_expiry():
    svc = SandboxCacheManagerService()
    svc.set("sb-1", "temp", "val", ttl=-1)
    assert svc.get("sb-1", "temp") is None


def test_l1_lru_eviction():
    svc = SandboxCacheManagerService(max_l1=3)
    svc.set("sb-1", "a", "1")
    svc.set("sb-1", "b", "2")
    svc.set("sb-1", "c", "3")
    svc.set("sb-1", "d", "4")  # evicts 'a' from L1
    # 'a' still in L2
    assert svc.get("sb-1", "a") == "1"  # L2 hit, promoted back


def test_l2_promotion():
    svc = SandboxCacheManagerService(max_l1=2)
    svc.set("sb-1", "a", "1")
    svc.set("sb-1", "b", "2")
    svc.set("sb-1", "c", "3")  # evicts 'a' from L1
    svc.get("sb-1", "a")  # promotes from L2 to L1
    stats = svc.get_stats("sb-1")
    assert stats["l2_hits"] >= 1


def test_delete():
    svc = SandboxCacheManagerService()
    svc.set("sb-1", "key", "val")
    assert svc.delete("sb-1", "key") is True
    assert svc.get("sb-1", "key") is None


def test_hit_rate():
    svc = SandboxCacheManagerService()
    svc.set("sb-1", "k", "v")
    svc.get("sb-1", "k")  # hit
    svc.get("sb-1", "k")  # hit
    svc.get("sb-1", "miss")  # miss
    stats = svc.get_stats("sb-1")
    assert stats["hit_rate"] == 66.7


def test_clear():
    svc = SandboxCacheManagerService()
    svc.set("sb-1", "a", "1")
    svc.set("sb-1", "b", "2")
    assert svc.clear("sb-1") == 2
