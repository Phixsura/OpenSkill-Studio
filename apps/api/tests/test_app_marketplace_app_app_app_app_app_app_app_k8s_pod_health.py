from app.services.app_marketplace_app_app_app_app_app_app_app_k8s_pod_health import analyze_pods

def test_pods():
    pods = [
        {"name": "api-abc", "status": "Running", "restarts": 0, "cpu_pct": 45, "mem_pct": 60},
        {"name": "api-def", "status": "Running", "restarts": 2, "cpu_pct": 55, "mem_pct": 70},
        {"name": "worker-xyz", "status": "CrashLoopBackOff", "restarts": 15, "cpu_pct": 0, "mem_pct": 0},
    ]
    r = analyze_pods(pods)
    assert r["running"] == 2
    assert r["failed"] == 1
    assert r["total_restarts"] == 17
    assert r["high_restart_pods"] == 1
    assert r["health"] == "degraded"
    assert r["avg_cpu_pct"] == 50.0
