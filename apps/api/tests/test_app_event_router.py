from app.services.app_event_router import route_event, group_by_installation

SUBS = [
    {"id": "s1", "event_type": "submission.completed", "enabled": True, "org_id": "o1", "installation_id": "i1"},
    {"id": "s2", "event_type": "submission.completed", "enabled": True, "org_id": "o2", "installation_id": "i2"},
    {"id": "s3", "event_type": "app.installed", "enabled": True, "org_id": "o1", "installation_id": "i3"},
    {"id": "s4", "event_type": "submission.completed", "enabled": False, "org_id": "o1", "installation_id": "i4"},
]

def test_route_by_type():
    matched = route_event(event_type="submission.completed", org_id="o1", subscriptions=SUBS)
    assert len(matched) == 1
    assert matched[0]["id"] == "s1"

def test_route_no_match():
    matched = route_event(event_type="unknown.event", org_id="o1", subscriptions=SUBS)
    assert len(matched) == 0

def test_disabled_excluded():
    matched = route_event(event_type="submission.completed", org_id="o1", subscriptions=SUBS)
    assert all(m["id"] != "s4" for m in matched)

def test_group():
    groups = group_by_installation(SUBS[:2])
    assert "i1" in groups
    assert "i2" in groups

def test_group_empty():
    assert group_by_installation([]) == {}
