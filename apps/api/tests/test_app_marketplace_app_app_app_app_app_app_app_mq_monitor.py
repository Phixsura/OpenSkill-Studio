from app.services.app_marketplace_app_app_app_app_app_app_app_mq_monitor import analyze_queues

def test_queues():
    queues = [
        {"name": "orders", "depth": 50, "enqueue_rate": 100, "dequeue_rate": 120, "consumers": 3},
        {"name": "emails", "depth": 5000, "enqueue_rate": 200, "dequeue_rate": 50, "consumers": 1},
        {"name": "dead_letter", "depth": 15000, "enqueue_rate": 5, "dequeue_rate": 0, "consumers": 0},
    ]
    r = analyze_queues(queues)
    assert r["queues"][0]["health"] == "healthy"
    assert r["queues"][1]["health"] == "warning"
    assert r["queues"][2]["health"] == "critical"
    assert r["overall_health"] == "critical"
    assert len(r["alerts"]) == 2
