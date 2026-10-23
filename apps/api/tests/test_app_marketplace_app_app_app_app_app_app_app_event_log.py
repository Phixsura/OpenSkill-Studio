from app.services.app_marketplace_app_app_app_app_app_app_app_event_log import EventLog

def test_event_log():
    log = EventLog()
    log.append(event_type="app.installed", source="marketplace", payload={"app": "test"}, actor="alice")
    log.append(event_type="app.installed", source="marketplace", payload={"app": "test2"}, actor="bob")
    log.append(event_type="user.created", source="auth", payload={"user": "carol"})
    r = log.query(event_type="app.installed")
    assert len(r) == 2
    counts = log.count_by_type()
    assert counts["app.installed"] == 2
    assert counts["user.created"] == 1
