from app.services.app_developer_activity import record_activity, get_recent_activity, get_activity_stats

def test_record():
    e = record_activity(developer_id="da1", action="create_app", resource="app/my-app")
    assert e["action"] == "create_app"

def test_recent():
    record_activity(developer_id="da2", action="publish", resource="app/x")
    assert len(get_recent_activity("da2")) >= 1

def test_limit():
    for i in range(50):
        record_activity(developer_id="da3", action="edit", resource=f"app/{i}")
    assert len(get_recent_activity("da3", limit=5)) == 5

def test_stats():
    record_activity(developer_id="da4", action="create", resource="a")
    record_activity(developer_id="da4", action="create", resource="b")
    record_activity(developer_id="da4", action="delete", resource="c")
    s = get_activity_stats("da4")
    assert s["total"] >= 3
    assert s["by_action"]["create"] >= 2

def test_empty():
    assert get_recent_activity("nobody") == []
