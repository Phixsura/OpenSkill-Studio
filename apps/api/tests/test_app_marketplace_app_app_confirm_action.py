from app.services.app_marketplace_app_app_confirm_action import require_confirmation

def test_low():
    r = require_confirmation(action="archive", resource_name="old-app", danger_level="low")
    assert not r["require_typing"]
    assert r["countdown_sec"] == 0

def test_high():
    r = require_confirmation(action="delete", resource_name="production-db", danger_level="high")
    assert r["require_typing"]
    assert r["confirm_word"] == "PRODUCTION-DB"
    assert "CANNOT be undone" in r["message"]
    assert r["countdown_sec"] == 5
