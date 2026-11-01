from app.services.app_marketplace_app_app_app_app_app_app_app_prio_sched import PriorityScheduler

def test_priority_order():
    ps = PriorityScheduler()
    ps.submit("r1", "low")
    ps.submit("r2", "critical")
    ps.submit("r3", "normal")
    assert ps.next()["id"] == "r2"
    assert ps.next()["id"] == "r3"
    assert ps.next()["id"] == "r1"

def test_stats():
    ps = PriorityScheduler()
    ps.submit("a", "high")
    ps.submit("b", "low")
    ps.next()
    s = ps.stats()
    assert s["total_queued"] == 1
    assert s["processed"] == 1
