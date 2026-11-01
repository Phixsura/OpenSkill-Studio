from app.services.app_marketplace_app_app_batch_operations import execute_batch, build_batch_summary

def test_execute():
    r = execute_batch(items=["app1", "app2", ""], action="delete")
    assert r["succeeded"] == 2
    assert r["failed"] == 1
    assert r["total"] == 3

def test_dry_run():
    r = execute_batch(items=["app1", "app2"], action="archive", dry_run=True)
    assert r["skipped"] == 2
    assert r["succeeded"] == 0

def test_summary():
    b1 = {"total": 10, "succeeded": 8}
    b2 = {"total": 5, "succeeded": 5}
    r = build_batch_summary(batches=[b1, b2])
    assert r["batch_count"] == 2
    assert r["total_items"] == 15
    assert r["success_rate"] == 86.7
