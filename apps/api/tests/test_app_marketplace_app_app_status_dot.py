from app.services.app_marketplace_app_app_status_dot import get_status_dot, get_aggregate_status_dot

def test_online():
    r = get_status_dot(status="online")
    assert r["color"] == "green"
    assert r["pulse"]

def test_error():
    r = get_status_dot(status="error")
    assert r["color"] == "red"

def test_aggregate_all_online():
    r = get_aggregate_status_dot(statuses=["online", "online"])
    assert r["status"] == "online"

def test_aggregate_error():
    r = get_aggregate_status_dot(statuses=["online", "error", "online"])
    assert r["status"] == "error"
