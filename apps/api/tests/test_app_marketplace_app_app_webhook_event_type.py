from app.services.app_marketplace_app_app_webhook_event_type import list_event_types, get_event_schema

def test_list_all():
    r = list_event_types()
    assert r["total"] == 8
    assert "Apps" in r["categories"]

def test_filter():
    r = list_event_types(category="Deployments")
    assert r["total"] == 3

def test_schema():
    r = get_event_schema(event_type="app.installed")
    assert "app_id" in r["fields"]
    assert "example" in r

def test_unknown():
    r = get_event_schema(event_type="nonexistent")
    assert "error" in r
