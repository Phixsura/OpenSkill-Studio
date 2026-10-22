from app.services.app_execution_scheduler import create_schedule, get_schedule, list_schedules, toggle_schedule, delete_schedule

def test_create():
    s = create_schedule(installation_id="i1", function_name="sync", cron_expression="0 * * * *")
    assert s["enabled"] is True
    assert s["cron"] == "0 * * * *"

def test_get():
    s = create_schedule(installation_id="i2", function_name="check", cron_expression="*/5 * * * *")
    assert get_schedule(s["id"]) is not None

def test_list():
    create_schedule(installation_id="i3", function_name="a", cron_expression="*")
    create_schedule(installation_id="i3", function_name="b", cron_expression="*")
    assert len(list_schedules("i3")) >= 2

def test_toggle():
    s = create_schedule(installation_id="i4", function_name="x", cron_expression="*")
    toggle_schedule(s["id"], False)
    assert get_schedule(s["id"])["enabled"] is False

def test_delete():
    s = create_schedule(installation_id="i5", function_name="y", cron_expression="*")
    assert delete_schedule(s["id"]) is True
    assert get_schedule(s["id"]) is None

def test_delete_missing():
    assert delete_schedule("nonexist") is False
