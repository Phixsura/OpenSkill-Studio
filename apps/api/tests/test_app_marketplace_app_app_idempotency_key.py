from app.services.app_marketplace_app_app_idempotency_key import IdempotencyStore, generate_idempotency_key

def test_first_request():
    store = IdempotencyStore()
    r = store.check_or_store(key="k1", request_hash="h1")
    assert not r["duplicate"]

def test_duplicate():
    store = IdempotencyStore()
    store.check_or_store(key="k1", request_hash="h1")
    store.store_response(key="k1", response={"id": "created"})
    r = store.check_or_store(key="k1", request_hash="h1")
    assert r["duplicate"]
    assert r["cached_response"]["id"] == "created"

def test_conflict():
    store = IdempotencyStore()
    store.check_or_store(key="k1", request_hash="h1")
    r = store.check_or_store(key="k1", request_hash="different")
    assert r["duplicate"]
    assert r["conflict"]

def test_generate():
    k = generate_idempotency_key()
    assert k.startswith("idem_")
    assert len(k) > 20
