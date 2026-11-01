from app.services.app_marketplace_app_app_app_app_app_app_app_hc_scheduler import HealthCheckScheduler
import time

def test_scheduler():
    hcs = HealthCheckScheduler()
    hcs.register("api", 30, "http://api/health")
    hcs.register("db", 60, "http://db/health")
    hcs.record_result("api", True)
    hcs.record_result("db", False)
    s = hcs.stats()
    assert s["healthy"] == 1
    assert s["unhealthy"] == 1

def test_due():
    hcs = HealthCheckScheduler()
    hcs.register("api", 30, "http://api/health")
    due = hcs.due_checks(now=time.time() + 31)
    assert len(due) == 1
