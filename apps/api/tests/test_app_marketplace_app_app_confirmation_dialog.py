from app.services.app_marketplace_app_app_confirmation_dialog import build_confirmation

def test_preset():
    r = build_confirmation(preset="delete_app")
    assert r["title"] == "Delete App"
    assert r["severity"] == "danger"
    assert r["confirm_text"] == "DELETE"

def test_custom():
    r = build_confirmation(title="Archive Project", message="This will archive the project", confirm_text="ARCHIVE")
    assert r["title"] == "Archive Project"
    assert r["requires_text_input"]

def test_unknown_preset():
    r = build_confirmation(preset="nonexistent", title="Custom", confirm_text="OK")
    assert r["preset"] is None
