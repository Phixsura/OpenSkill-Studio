from app.services.app_marketplace_app_app_app_app_app_app_app_task_scheduler import (
    create_task, run_task, list_tasks, toggle_task, clear_tasks,
)

def test_lifecycle():
    clear_tasks()
    create_task("cleanup", "0 * * * *", "tasks.cleanup")
    create_task("report", "0 9 * * 1", "tasks.report")
    assert len(list_tasks()) == 2
    r = run_task("cleanup")
    assert r["ran"]
    assert r["run_count"] == 1
    toggle_task("cleanup")
    r2 = run_task("cleanup")
    assert not r2["ran"]
    assert r2["error"] == "disabled"
    clear_tasks()
