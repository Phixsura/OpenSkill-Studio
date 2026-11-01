from app.services.app_marketplace_toast_notifications import create_toast, create_action_toast, build_toast_queue

def test_create():
    t = create_toast(type="success", title="Saved!", message="Changes saved")
    assert t["icon"] == "✅"
    assert t["visible"]

def test_invalid_type():
    t = create_toast(type="custom", title="X")
    assert t["type"] == "info"

def test_action_install():
    t = create_action_toast(action="install", entity="MyApp", success=True)
    assert t["type"] == "success"
    assert "MyApp" in t["title"]

def test_action_fail():
    t = create_action_toast(action="deploy", entity="App", success=False)
    assert t["type"] == "error"
    assert "failed" in t["title"].lower()

def test_queue():
    toasts = [{"visible": True}] * 5
    q = build_toast_queue(toasts=toasts, max_visible=3)
    assert len(q["visible"]) == 3
    assert q["queued"] == 2
