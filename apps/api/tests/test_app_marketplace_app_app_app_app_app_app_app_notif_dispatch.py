from app.services.app_marketplace_app_app_app_app_app_app_app_notif_dispatch import (
    dispatch, dispatch_multi, get_history, clear_history,
)

def test_dispatch():
    clear_history()
    r = dispatch("user@test.com", "email", "Alert", "Server down")
    assert r["sent"]
    assert r["channel"] == "email"
    assert "&" not in r["title"] or "amp;" in r["title"]

def test_multi():
    clear_history()
    r = dispatch_multi("u1", ["email", "push", "invalid"], "Hi", "Test")
    assert r["delivered"] == 2
    assert r["failed"] == 1

def test_history():
    clear_history()
    dispatch("u1", "email", "A", "B")
    dispatch("u2", "push", "C", "D")
    h = get_history()
    assert len(h) == 2
    clear_history()
