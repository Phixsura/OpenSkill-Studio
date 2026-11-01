from app.services.app_marketplace_app_app_app_app_app_app_app_event_types import list_event_types, list_groups, search_event_types

def test_list_all():
    all_types = list_event_types()
    assert len(all_types) == 13

def test_by_group():
    app_types = list_event_types(group="app")
    assert len(app_types) == 4
    assert all("app." in t["type"] for t in app_types)

def test_groups():
    groups = list_groups()
    assert "app" in groups
    assert "billing" in groups
    assert len(groups) == 4

def test_search():
    r = search_event_types("deploy")
    assert len(r) == 3
    r2 = search_event_types("payment")
    assert len(r2) == 2
