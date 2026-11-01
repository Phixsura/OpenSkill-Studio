from app.services.app_marketplace_app_app_app_app_app_app_app_worker_pool import create_pool, process_job, pool_health

def test_process():
    p = create_pool("workers", 3)
    r = process_job(p)
    assert r["processed"]
    assert p["processed"] == 1

def test_health():
    p = create_pool("workers", 5, queue_depth=0)
    p["processed"] = 100
    p["failed"] = 2
    r = pool_health(p)
    assert r["healthy"]
    assert r["failure_rate"] == 2.0
