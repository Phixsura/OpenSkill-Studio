from app.services.app_webhook_delivery_log import log_delivery, get_delivery_log, get_failure_log, get_success_rate

APP = "wdl-test"

def test_log():
    e = log_delivery(app_id=APP, event_type="app.installed", url="https://x.com", status_code=200, success=True, duration_ms=100, attempt=1)
    assert e["success"] is True

def test_get_log():
    log_delivery(app_id="gl-app", event_type="t", url="u", status_code=200, success=True, duration_ms=50, attempt=1)
    assert len(get_delivery_log("gl-app")) >= 1

def test_failure_log():
    app = "fl-app"
    log_delivery(app_id=app, event_type="t", url="u", status_code=200, success=True, duration_ms=50, attempt=1)
    log_delivery(app_id=app, event_type="t", url="u", status_code=500, success=False, duration_ms=100, attempt=1)
    failures = get_failure_log(app)
    assert len(failures) >= 1
    assert all(not f["success"] for f in failures)

def test_success_rate():
    app = "sr-app"
    for _ in range(8):
        log_delivery(app_id=app, event_type="t", url="u", status_code=200, success=True, duration_ms=50, attempt=1)
    for _ in range(2):
        log_delivery(app_id=app, event_type="t", url="u", status_code=500, success=False, duration_ms=100, attempt=1)
    assert get_success_rate(app) == 80.0

def test_empty_rate():
    assert get_success_rate("empty-app") == 100.0
