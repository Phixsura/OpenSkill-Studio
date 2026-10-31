from app.services.app_marketplace_webhook_log import create_log_entry, compute_delivery_stats

def test_success_entry():
    e = create_log_entry(webhook_id="w1", event_type="install", url="https://x.com/hook",
                          status_code=200, response_time_ms=150, payload_size=1024)
    assert e["success"]

def test_failure_entry():
    e = create_log_entry(webhook_id="w1", event_type="install", url="https://x.com/hook",
                          status_code=500, response_time_ms=5000, payload_size=0)
    assert not e["success"]

def test_stats():
    logs = [{"success": True, "response_time_ms": 100}, {"success": True, "response_time_ms": 200},
            {"success": False, "response_time_ms": 5000}]
    s = compute_delivery_stats(logs=logs)
    assert s["total"] == 3
    assert s["success_rate"] < 70
    assert s["failures"] == 1

def test_empty_stats():
    s = compute_delivery_stats(logs=[])
    assert s["total"] == 0
