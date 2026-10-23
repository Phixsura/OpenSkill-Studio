from app.services.app_marketplace_app_app_toast_notification import create_toast

def test_success():
    r = create_toast(message="App published!", toast_type="success")
    assert r["icon"] == "✅"
    assert r["duration_ms"] == 3000
    assert r["message"] == "App published!"

def test_error():
    r = create_toast(message="Deploy failed", toast_type="error", action_label="Retry")
    assert r["icon"] == "❌"
    assert r["action_label"] == "Retry"
    assert r["duration_ms"] == 5000

def test_default():
    r = create_toast(message="Hello")
    assert r["type"] == "info"
