from app.services.app_marketplace_app_app_app_app_app_app_app_req_batch import RequestBatcher

def test_auto_flush():
    rb = RequestBatcher(max_batch_size=3)
    rb.add({"id": 1})
    rb.add({"id": 2})
    r = rb.add({"id": 3})
    assert r["flushed"]
    assert r["batch_size"] == 3
    assert rb.stats()["buffer_size"] == 0

def test_manual_flush():
    rb = RequestBatcher(max_batch_size=10)
    rb.add({"id": 1})
    rb.add({"id": 2})
    r = rb.flush()
    assert r["batch_size"] == 2
    assert rb.stats()["batches_flushed"] == 1
