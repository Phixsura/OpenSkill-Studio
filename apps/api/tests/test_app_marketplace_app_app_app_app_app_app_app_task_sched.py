from app.services.app_marketplace_app_app_app_app_app_app_app_task_sched import TaskScheduler

def test_tick():
    ts = TaskScheduler()
    ts.schedule("cleanup", 60, "cleanup_handler")
    ts.schedule("report", 300, "report_handler")
    triggered = ts.tick(now=1000)
    assert len(triggered) == 2  # both trigger (1000-0 >= 60 and >= 300)
    triggered2 = ts.tick(now=1050)
    assert len(triggered2) == 0  # not enough time
    triggered3 = ts.tick(now=1061)
    assert len(triggered3) == 1  # only cleanup (61s passed)
    assert triggered3[0]["task"] == "cleanup"

def test_disable():
    ts = TaskScheduler()
    ts.schedule("job", 10, "handler")
    ts.disable("job")
    triggered = ts.tick(now=100)
    assert len(triggered) == 0
    assert ts.stats()["enabled"] == 0
