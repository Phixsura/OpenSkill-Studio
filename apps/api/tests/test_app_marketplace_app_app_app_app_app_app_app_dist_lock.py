from app.services.app_marketplace_app_app_app_app_app_app_app_dist_lock import (
    acquire_lock, release_lock, extend_lock, list_locks, clear_locks,
)

def test_acquire_release():
    clear_locks()
    r = acquire_lock("db:migrate", "worker-1")
    assert r["acquired"]
    r2 = acquire_lock("db:migrate", "worker-2")
    assert not r2["acquired"]
    assert r2["held_by"] == "worker-1"
    release_lock("db:migrate", r["token"])
    r3 = acquire_lock("db:migrate", "worker-2")
    assert r3["acquired"]
    clear_locks()

def test_extend():
    clear_locks()
    r = acquire_lock("res", "me", ttl_sec=10)
    e = extend_lock("res", r["token"], extra_sec=20)
    assert e["extended"]
    assert e["new_ttl"] > 25
    clear_locks()
