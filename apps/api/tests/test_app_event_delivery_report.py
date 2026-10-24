from app.services.app_event_delivery_report import compute_delivery_report

def test_basic():
    deliveries = [
        {"event_type": "app.installed", "status": "delivered"},
        {"event_type": "app.installed", "status": "delivered"},
        {"event_type": "app.installed", "status": "failed"},
        {"event_type": "submission.completed", "status": "delivered"},
    ]
    r = compute_delivery_report(deliveries)
    assert r["total_deliveries"] == 4
    app = next(e for e in r["event_types"] if e["event_type"] == "app.installed")
    assert app["delivered"] == 2
    assert app["failed"] == 1
    assert app["success_rate"] == round(2/3*100, 1)

def test_empty():
    r = compute_delivery_report([])
    assert r["total_deliveries"] == 0
    assert r["event_types"] == []

def test_all_success():
    r = compute_delivery_report([{"event_type": "x", "status": "delivered"} for _ in range(5)])
    assert r["event_types"][0]["success_rate"] == 100.0
