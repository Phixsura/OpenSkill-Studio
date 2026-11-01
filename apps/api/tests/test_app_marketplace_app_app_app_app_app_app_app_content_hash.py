from app.services.app_marketplace_app_app_app_app_app_app_app_content_hash import compute_hash, verify_integrity, batch_verify

def test_compute():
    r = compute_hash("hello world")
    assert len(r["hash"]) == 64
    assert r["algorithm"] == "sha256"

def test_verify():
    h = compute_hash("test data")["hash"]
    r = verify_integrity("test data", h)
    assert r["match"]
    r2 = verify_integrity("wrong data", h)
    assert not r2["match"]

def test_batch():
    h1 = compute_hash("a")["hash"]
    h2 = compute_hash("b")["hash"]
    r = batch_verify([
        {"name": "file1", "content": "a", "expected_hash": h1},
        {"name": "file2", "content": "b", "expected_hash": "wrong"},
    ])
    assert r["passed"] == 1
    assert r["failed"] == 1
    assert not r["all_valid"]
