from app.services.app_marketplace_app_webhook_debugger import capture_delivery_attempt, diagnose_failure, build_replay_request

def test_capture_success():
    r = capture_delivery_attempt(webhook_id="w1", event_type="app.installed", url="https://x.com/hook",
                                  payload_size=512, response={"status_code": 200, "duration_ms": 50})
    assert r["success"]

def test_capture_failure():
    r = capture_delivery_attempt(webhook_id="w1", event_type="app.installed", url="https://x.com/hook",
                                  payload_size=512, response={"status_code": 500, "duration_ms": 100})
    assert not r["success"]

def test_diagnose_auth():
    d = diagnose_failure(attempt={"status_code": 401})
    assert d["cause"] == "authentication"

def test_diagnose_timeout():
    d = diagnose_failure(attempt={"status_code": 200, "response_time_ms": 15000})
    assert d["cause"] == "timeout"

def test_replay():
    r = build_replay_request(original={"url": "https://x.com/hook", "event_type": "app.installed"})
    assert r["headers"]["X-Replay"] == "true"
