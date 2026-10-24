from app.services.app_marketplace_scheduled_task import validate_cron, create_scheduled_task, list_scheduled_tasks

def test_valid_cron():
    r = validate_cron(expression="0 3 * * *")
    assert r["valid"]

def test_invalid_cron():
    r = validate_cron(expression="bad cron")
    assert not r["valid"]

def test_create():
    r = create_scheduled_task(app_id="a1", name="Cleanup", cron="0 3 * * *", endpoint="/api/cleanup")
    assert r["task_id"].startswith("task_")
    assert r["status"] == "active"

def test_create_bad_cron():
    r = create_scheduled_task(app_id="a1", name="X", cron="x", endpoint="/api/x")
    assert "error" in r

def test_list():
    r = list_scheduled_tasks(app_id="a1")
    assert r["total"] == 2
