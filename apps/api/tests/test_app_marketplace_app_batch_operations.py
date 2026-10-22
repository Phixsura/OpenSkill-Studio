from app.services.app_marketplace_app_batch_operations import create_batch_job, execute_batch, get_batch_progress

def test_create():
    j = create_batch_job(operation="restart", target_ids=["i1", "i2"])
    assert j["total"] == 2
    assert j["status"] == "pending"

def test_invalid_op():
    j = create_batch_job(operation="destroy", target_ids=["i1"])
    assert j["error"]

def test_no_targets():
    j = create_batch_job(operation="restart", target_ids=[])
    assert j["error"]

def test_execute():
    job = {"targets": ["i1", "i2", "i3"]}
    r = execute_batch(job=job)
    assert r["succeeded"] == 3

def test_progress():
    p = get_batch_progress(total=10, completed=7)
    assert p["pct"] == 70
    assert p["remaining"] == 3
