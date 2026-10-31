from app.services.app_marketplace_app_webhook_event_catalog import list_event_catalog, get_event_detail

def test_list_all():
    r = list_event_catalog()
    assert r["total_events"] == 9
    assert len(r["categories"]) == 3

def test_filter():
    r = list_event_catalog(category="billing")
    assert r["total_events"] == 3

def test_invalid_cat():
    r = list_event_catalog(category="magic")
    assert "error" in r

def test_detail():
    r = get_event_detail(event_name="app.installed")
    assert r["found"]
    assert "app_id" in r["payload_example"]

def test_not_found():
    r = get_event_detail(event_name="unknown.event")
    assert not r["found"]
