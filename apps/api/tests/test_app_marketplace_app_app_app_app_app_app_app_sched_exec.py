from app.services.app_marketplace_app_app_app_app_app_app_app_sched_exec import ScheduledTaskExecutor

def test_execute():
    ste = ScheduledTaskExecutor()
    ste.register("cleanup", "0 * * * *", lambda: {"cleaned": 5})
    r = ste.execute("cleanup")
    assert r["executed"]
    assert r["output"]["cleaned"] == 5
    assert ste.stats()["total_runs"] == 1

def test_disabled():
    ste = ScheduledTaskExecutor()
    ste.register("task", "*/5 * * * *")
    ste.disable("task")
    r = ste.execute("task")
    assert not r["executed"]
