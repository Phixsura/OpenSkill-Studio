from app.services.app_marketplace_app_scheduler import create_scheduled_task, describe_schedule, list_upcoming_runs

def test_create():
    t = create_scheduled_task(installation_id="i1", name="daily-sync", cron_expr="0 0 * * *", action="sync")
    assert t["status"] == "active"

def test_invalid_cron():
    t = create_scheduled_task(installation_id="i1", name="bad", cron_expr="not valid", action="x")
    assert t["error"]

def test_short_name():
    t = create_scheduled_task(installation_id="i1", name="ab", cron_expr="* * * * *", action="x")
    assert t["error"]

def test_describe_hourly():
    assert describe_schedule(cron_expr="0 * * * *") == "Every hour"

def test_describe_daily():
    assert describe_schedule(cron_expr="0 0 * * *") == "Daily at midnight"

def test_list():
    tasks = [{"name": "sync", "cron_expr": "0 * * * *", "status": "active"},
             {"name": "cleanup", "cron_expr": "0 0 * * *", "status": "paused"}]
    r = list_upcoming_runs(tasks=tasks)
    assert len(r) == 1
