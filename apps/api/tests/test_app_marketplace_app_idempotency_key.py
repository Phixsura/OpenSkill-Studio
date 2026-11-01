from app.services.app_marketplace_app_idempotency_key import (
    generate_idempotency_key, check_idempotency, compute_request_hash)

def test_generate():
    r = generate_idempotency_key(prefix="pay")
    assert r["key"].startswith("pay_")
    assert len(r["key"]) > 20

def test_check_new():
    r = check_idempotency(key="k1", cache={})
    assert not r["duplicate"]
    assert r["status"] == "new"

def test_check_duplicate():
    cache = {"k1": {"response": {"id": "order_1"}, "created_at": "2026-10-23T12:00:00"}}
    r = check_idempotency(key="k1", cache=cache)
    assert r["duplicate"]
    assert r["original_response"]["id"] == "order_1"

def test_hash():
    h1 = compute_request_hash(method="POST", path="/api/orders", body='{"amount":100}')
    h2 = compute_request_hash(method="POST", path="/api/orders", body='{"amount":100}')
    assert h1["hash"] == h2["hash"]
    h3 = compute_request_hash(method="POST", path="/api/orders", body='{"amount":200}')
    assert h1["hash"] != h3["hash"]
