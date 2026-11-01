from app.services.app_marketplace_app_app_app_app_app_app_app_cron_monitor import CronMonitor

def test_monitor():
    cm = CronMonitor()
    cm.register("cleanup", "0 * * * *")
    cm.register("report", "0 9 * * *")
    cm.record_run("cleanup", True, 500)
    cm.record_run("cleanup", True, 450)
    cm.record_run("report", False, 3000)
    assert len(cm.failing_jobs()) == 1
    s = cm.stats()
    assert s["total_runs"] == 3
    assert s["success_rate"] == 66.7
