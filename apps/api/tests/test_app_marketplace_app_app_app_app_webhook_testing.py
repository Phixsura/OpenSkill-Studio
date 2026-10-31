from app.services.app_marketplace_app_app_app_app_webhook_testing import generate_test_payload, build_test_result

def test_generate():
    r = generate_test_payload(event_type="app.installed")
    assert r["event_type"] == "app.installed"
    assert r["payload"]["type"] == "app.installed"
    assert r["size_bytes"] > 0

def test_result_success():
    r = build_test_result(status_code=200, duration_ms=85)
    assert r["success"]
    assert "✅" in r["verdict"]

def test_result_failure():
    r = build_test_result(status_code=500, error="Internal server error")
    assert not r["success"]
    assert "❌" in r["verdict"]
