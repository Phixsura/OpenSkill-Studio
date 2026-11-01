from app.services.app_webhook_test_result import format_test_result

def test_success():
    r = format_test_result(success=True, status_code=200, duration_ms=50, response_body='{"ok":true}', error=None)
    assert "working" in r["verdict"]

def test_failure():
    r = format_test_result(success=False, status_code=500, duration_ms=100, response_body=None, error="Internal error")
    assert "Internal error" in r["verdict"]

def test_truncate():
    r = format_test_result(success=True, status_code=200, duration_ms=10, response_body="x" * 1000, error=None)
    assert len(r["response_preview"]) <= 500
