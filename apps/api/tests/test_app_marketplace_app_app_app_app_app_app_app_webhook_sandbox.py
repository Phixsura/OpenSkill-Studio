from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_sandbox import (
    create_test_event, simulate_delivery, delivery_report,
)

def test_event_delivery():
    event = create_test_event("app.installed", {"app_id": "123"})
    assert event["test"]
    assert len(event["event_id"]) == 12
    d = simulate_delivery(event, "https://hook.example.com")
    assert d["delivered"]
    assert d["status_code"] == 200

def test_report():
    deliveries = [
        {"delivered": True, "response_ms": 50},
        {"delivered": True, "response_ms": 30},
        {"delivered": False, "response_ms": 5000},
    ]
    r = delivery_report(deliveries)
    assert r["succeeded"] == 2
    assert r["success_rate"] == 67
