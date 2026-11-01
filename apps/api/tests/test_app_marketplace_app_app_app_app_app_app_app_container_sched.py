from app.services.app_marketplace_app_app_app_app_app_app_app_container_sched import schedule_container, cluster_utilization

def test_schedule():
    r = schedule_container(
        {"name": "web", "cpu": 2, "memory_mb": 1024},
        [{"name": "n1", "cpu_total": 4, "cpu_used": 3, "memory_mb_total": 4096, "memory_mb_used": 1024},
         {"name": "n2", "cpu_total": 8, "cpu_used": 2, "memory_mb_total": 8192, "memory_mb_used": 2048}])
    assert r["scheduled"]
    assert r["node"] == "n2"

def test_no_capacity():
    r = schedule_container(
        {"name": "big", "cpu": 16, "memory_mb": 32768},
        [{"name": "n1", "cpu_total": 4, "cpu_used": 0, "memory_mb_total": 4096, "memory_mb_used": 0}])
    assert not r["scheduled"]

def test_utilization():
    r = cluster_utilization([
        {"cpu_total": 8, "cpu_used": 4, "memory_mb_total": 16384, "memory_mb_used": 8192},
        {"cpu_total": 8, "cpu_used": 6, "memory_mb_total": 16384, "memory_mb_used": 12288},
    ])
    assert r["cpu_pct"] == 62.5
    assert r["nodes"] == 2
