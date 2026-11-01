from app.services.app_marketplace_webhook_payload_builder import build_webhook_payload, add_delivery_metadata, validate_payload_size

def test_build():
    p = build_webhook_payload(event_type="app.installed", data={"org_id": "o1"}, app_id="a1")
    assert p["event"] == "app.installed"
    assert p["id"].startswith("evt_")

def test_delivery():
    p = build_webhook_payload(event_type="test", data={}, app_id="a1")
    r = add_delivery_metadata(payload=p, attempt=1, max_attempts=5, webhook_url="https://x.com")
    assert r["delivery"]["attempt"] == 1
    assert r["delivery"]["idempotency_key"].endswith("_1")

def test_size_ok():
    p = {"event": "test", "data": {"small": True}}
    r = validate_payload_size(payload=p)
    assert r["within_limit"]

def test_size_exceeded():
    p = {"data": "x" * 300000}
    r = validate_payload_size(payload=p, max_bytes=256000)
    assert not r["within_limit"]
