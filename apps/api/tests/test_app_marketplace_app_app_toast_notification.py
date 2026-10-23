from app.services.app_marketplace_app_app_toast_notification import create_toast, build_toast_queue

def test_create():
    r = create_toast(message="App published!", type="success")
    assert r["id"].startswith("toast_")
    assert r["icon"] == "✅"
    assert r["type"] == "success"

def test_action():
    r = create_toast(message="Update available", type="info", action_label="Update now")
    assert r["action_label"] == "Update now"

def test_queue():
    toasts = [create_toast(message=f"Toast {i}") for i in range(5)]
    r = build_toast_queue(toasts=toasts, max_visible=3)
    assert r["visible_count"] == 3
    assert r["queued_count"] == 2
