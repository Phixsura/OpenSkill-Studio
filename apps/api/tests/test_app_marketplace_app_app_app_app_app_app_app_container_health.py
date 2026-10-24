from app.services.app_marketplace_app_app_app_app_app_app_app_container_health import check_container, cluster_health

def test_healthy():
    r = check_container("api", 45, 256, 512, 0)
    assert r["healthy"]
    assert r["memory_pct"] == 50.0
    assert len(r["issues"]) == 0

def test_unhealthy():
    r = check_container("worker", 98, 480, 512, 8, "running")
    assert not r["healthy"]
    assert len(r["issues"]) >= 2

def test_cluster():
    containers = [
        check_container("a", 30, 128, 512, 0),
        check_container("b", 90, 450, 512, 10),
    ]
    r = cluster_health(containers)
    assert r["healthy"] == 1
    assert r["total_restarts"] == 10
