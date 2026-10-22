from app.services.app_uninstall_summary import build_uninstall_summary

def test_with_data():
    s = build_uninstall_summary(app_name="App", installation={"org_id": "o1"},
        active_subscriptions=3, active_automations=1, secrets_count=2)
    assert s["is_destructive"] is True
    assert len(s["warnings"]) == 3

def test_clean():
    s = build_uninstall_summary(app_name="App", installation={"org_id": "o1"},
        active_subscriptions=0, active_automations=0, secrets_count=0)
    assert s["is_destructive"] is False
