from app.services.app_marketplace_app_app_app_app_app_app_app_queue_monitor import create_queue_stats, aggregate_queues

def test_stats():
    q = create_queue_stats("emails", pending=50, processing=10, completed=900, failed=40, avg_latency_ms=150)
    assert q["total"] == 1000
    assert q["health"] == "healthy"
    assert q["error_rate"] == 4.0

def test_aggregate():
    queues = [
        create_queue_stats("emails", 50, 10, 900, 40),
        create_queue_stats("webhooks", 2000, 5, 500, 100),
    ]
    r = aggregate_queues(queues)
    assert r["queue_count"] == 2
    assert r["total_pending"] == 2050
    assert not r["all_healthy"]
    assert "webhooks" in r["unhealthy_queues"]
