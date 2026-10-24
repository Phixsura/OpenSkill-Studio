from app.services.app_marketplace_app_app_app_app_app_app_app_toast_system import create_toast, create_batch

def test_toast():
    t = create_toast(title="Saved!", variant="success")
    assert t["icon"] == "✅"
    assert t["duration_ms"] == 3000
    assert t["id"].startswith("toast_")

def test_error():
    t = create_toast(title="Failed", message="Connection lost", variant="error")
    assert t["duration_ms"] == 5000
    assert t["color"] == "red"

def test_batch():
    batch = create_batch([
        {"title": "A", "variant": "success"},
        {"title": "B", "variant": "error"},
    ])
    assert len(batch) == 2
    assert batch[0]["variant"] == "success"
