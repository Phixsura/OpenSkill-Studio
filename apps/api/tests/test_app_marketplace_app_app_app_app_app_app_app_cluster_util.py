from app.services.app_marketplace_app_app_app_app_app_app_app_cluster_util import cluster_utilization

def test_util():
    r = cluster_utilization([
        {"cpu_capacity": 100, "cpu_used": 40, "mem_capacity_gb": 256, "mem_used_gb": 128},
        {"cpu_capacity": 100, "cpu_used": 60, "mem_capacity_gb": 256, "mem_used_gb": 200},
    ])
    assert r["cluster_count"] == 2
    assert r["cpu"]["pct"] == 50.0
    assert r["memory"]["pct"] == 64.1
    assert r["overall_health"] == "healthy"
