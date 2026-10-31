from app.services.app_marketplace_app_app_app_app_app_app_app_chaos_sched import ChaosScheduler

def test_lifecycle():
    cs = ChaosScheduler()
    cs.schedule("exp-1", "api", "latency", 30, "single")
    cs.start("exp-1")
    assert cs._experiments["exp-1"]["status"] == "running"
    cs.stop("exp-1")
    assert cs._experiments["exp-1"]["status"] == "completed"

def test_abort():
    cs = ChaosScheduler()
    cs.schedule("exp-2", "db", "partition")
    cs.start("exp-2")
    cs.abort("exp-2")
    s = cs.stats()
    assert s["by_status"]["aborted"] == 1

def test_list():
    cs = ChaosScheduler()
    cs.schedule("a", "x", "latency")
    cs.schedule("b", "y", "error")
    cs.start("a")
    assert len(cs.list_experiments("running")) == 1
