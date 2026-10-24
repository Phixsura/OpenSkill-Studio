from app.services.app_marketplace_app_queue_monitor import get_queue_status, get_dead_letter_queue

def test_status():
    queues = [
        {"name": "email", "pending": 50, "processing": 5, "failed": 1, "completed": 1000, "throughput_per_min": 20},
        {"name": "webhook", "pending": 0, "processing": 0, "failed": 0, "completed": 500, "throughput_per_min": 10},
    ]
    r = get_queue_status(queues=queues)
    assert r["total_backlog"] == 50
    assert r["all_healthy"]
    assert r["queues"][0]["eta_min"] == 2.5

def test_unhealthy():
    queues = [{"name": "bad", "pending": 0, "processing": 0, "failed": 50, "completed": 50, "throughput_per_min": 5}]
    r = get_queue_status(queues=queues)
    assert not r["all_healthy"]

def test_dlq():
    items = [{"id": "j1", "error": "timeout", "failed_at": "2026-10-23"}]
    r = get_dead_letter_queue(items=items)
    assert r["total"] == 1
