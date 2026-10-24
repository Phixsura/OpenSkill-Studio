from app.services.app_marketplace_app_app_app_app_app_app_app_notif_prefs_page import build_notification_prefs

def test_defaults():
    r = build_notification_prefs()
    assert len(r["categories"]) == 6
    assert len(r["channels"]) == 4
    sec = next(c for c in r["categories"] if c["id"] == "security")
    assert all(sec["channels"].values())  # forced on
    assert not sec["editable"]

def test_overrides():
    r = build_notification_prefs({"deploys": {"email": False, "slack": True}})
    dep = next(c for c in r["categories"] if c["id"] == "deploys")
    assert not dep["channels"]["email"]
    assert dep["channels"]["slack"]
