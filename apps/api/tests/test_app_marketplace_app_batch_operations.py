from app.services.app_marketplace_app_batch_operations import create_batch, get_batch_progress

def test_create():
    r = create_batch(operation="tag", resource_ids=["a1", "a2", "a3"], params={"tag": "v2"})
    assert r["batch_id"].startswith("batch_")
    assert r["resource_count"] == 3

def test_invalid_op():
    r = create_batch(operation="nuke", resource_ids=["a1"])
    assert "error" in r

def test_too_many():
    r = create_batch(operation="delete", resource_ids=[f"a{i}" for i in range(200)])
    assert "error" in r

def test_progress():
    r = get_batch_progress(total=10, completed=7, failed=1)
    assert r["progress_pct"] == 70.0
    assert r["remaining"] == 2
    assert r["status"] == "in_progress"

def test_done():
    r = get_batch_progress(total=5, completed=4, failed=1)
    assert r["status"] == "completed"
