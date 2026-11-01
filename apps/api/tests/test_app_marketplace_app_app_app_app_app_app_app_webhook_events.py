from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_events import list_events, validate_subscription

def test_list():
    r = list_events()
    assert r["total"] == 10
    assert "lifecycle" in r["categories"]
    r2 = list_events("billing")
    assert r2["total"] == 2

def test_validate():
    r = validate_subscription(["app.installed", "user.created", "fake.event"])
    assert r["valid_count"] == 2
    assert not r["all_valid"]
    assert "fake.event" in r["invalid"]
