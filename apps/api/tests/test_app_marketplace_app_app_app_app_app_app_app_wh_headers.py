from app.services.app_marketplace_app_app_app_app_app_app_app_wh_headers import build_webhook_headers, verify_webhook_headers

def test_build_verify():
    secret = "test_secret_key"
    payload = '{"event":"test"}'
    headers = build_webhook_headers(payload=payload, secret=secret, event_type="app.installed")
    assert headers["X-Webhook-Signature"].startswith("v1=")
    assert headers["X-Webhook-Event"] == "app.installed"
    assert headers["Content-Type"] == "application/json"
    # Verify
    r = verify_webhook_headers(headers=headers, payload=payload, secret=secret)
    assert r["valid"]
    assert r["event"] == "app.installed"

def test_invalid():
    r = verify_webhook_headers(headers={"X-Webhook-Timestamp": "0", "X-Webhook-Signature": "v1=bad"},
                                 payload="test", secret="secret")
    assert not r["valid"]
