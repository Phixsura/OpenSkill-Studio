from app.services.app_marketplace_app_app_webhook_retry import plan_retries, build_delivery_report

def test_retry_schedule():
    r = plan_retries(max_attempts=4, base_delay_s=60)
    assert len(r["schedule"]) == 4
    assert r["schedule"][0]["delay_s"] == 60
    assert r["schedule"][1]["delay_s"] == 120
    assert r["schedule"][2]["delay_s"] == 240

def test_delivery_success():
    deliveries = [
        {"attempt": 1, "status_code": 500, "response_ms": 100, "error": "Server error"},
        {"attempt": 2, "status_code": 200, "response_ms": 50},
    ]
    r = build_delivery_report(deliveries=deliveries)
    assert r["final_success"]
    assert r["status"] == "delivered"
    assert r["total_attempts"] == 2

def test_delivery_fail():
    deliveries = [{"attempt": 1, "status_code": 500}, {"attempt": 2, "status_code": 500}]
    r = build_delivery_report(deliveries=deliveries)
    assert not r["final_success"]
    assert r["status"] == "failed"
