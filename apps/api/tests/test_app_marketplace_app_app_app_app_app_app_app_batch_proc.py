from app.services.app_marketplace_app_app_app_app_app_app_app_batch_proc import process_batch, estimate_time

def test_process():
    r = process_batch(list(range(10)), batch_size=3, processor=lambda b: {"sum": sum(b)})
    assert r["total_items"] == 10
    assert r["total_batches"] == 4
    assert r["failed_batches"] == 0
    assert r["batches"][0]["output"]["sum"] == 3  # 0+1+2

def test_failure():
    def bad_proc(batch):
        if 5 in batch:
            raise ValueError("bad item")
        return {"ok": True}
    r = process_batch(list(range(8)), batch_size=3, processor=bad_proc)
    assert r["failed_batches"] == 1

def test_estimate():
    r = estimate_time(10000, 100, 50.0)
    assert r["num_batches"] == 100
    assert r["estimated_ms"] == 5000.0
