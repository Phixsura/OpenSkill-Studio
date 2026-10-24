from app.services.app_marketplace_app_app_app_app_app_app_app_wh_tester import build_test_event, evaluate_response

def test_event():
    e = build_test_event("app.installed")
    assert e["type"] == "app.installed"
    assert e["test"]
    assert e["id"].startswith("evt_test_")

def test_success():
    r = evaluate_response(status_code=200, response_body='{"ok":true}', latency_ms=150)
    assert r["success"]
    assert r["grade"] == "A"
    assert r["is_json"]

def test_failure():
    r = evaluate_response(status_code=500, response_body="error", latency_ms=3000)
    assert not r["success"]
    assert r["grade"] == "F"
    assert "HTTP 500" in r["issues"]

def test_timeout():
    r = evaluate_response(status_code=200, response_body="", latency_ms=6000)
    assert not r["success"]
    assert r["timed_out"]
