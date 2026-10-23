from app.services.app_marketplace_app_app_webhook_inspector import inspect_webhook_delivery

def test_json_body():
    r = inspect_webhook_delivery(
        headers={"content-type": "application/json", "x-signature": "abc123"},
        body='{"event":"app.installed","app_id":"a1"}',
        status_code=200, duration_ms=85)
    assert r["is_json"]
    assert r["body_parsed"]["event"] == "app.installed"
    assert r["success"]
    assert r["header_count"] == 2

def test_non_json():
    r = inspect_webhook_delivery(headers={"content-type": "text/plain"},
                                  body="OK", status_code=200, duration_ms=10)
    assert not r["is_json"]
    assert r["body_parsed"] is None

def test_failure():
    r = inspect_webhook_delivery(headers={}, body="error", status_code=500, duration_ms=3000)
    assert not r["success"]
