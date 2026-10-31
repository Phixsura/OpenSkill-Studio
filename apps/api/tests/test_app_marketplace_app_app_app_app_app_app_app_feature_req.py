from app.services.app_marketplace_app_app_app_app_app_app_app_feature_req import (
    submit_request, vote, top_requests, request_stats, clear_requests,
)

def test_submit_vote():
    clear_requests()
    r = submit_request("Dark mode", "Add dark theme", "alice", "ui")
    assert r["id"] == 1
    vote(1, "bob")
    vote(1, "carol")
    r2 = vote(1, "bob")
    assert not r2["voted"]  # duplicate
    top = top_requests()
    assert top[0]["votes"] == 3
    clear_requests()

def test_stats():
    clear_requests()
    submit_request("A", "desc", "u1", "ui")
    submit_request("B", "desc", "u2", "api")
    s = request_stats()
    assert s["total"] == 2
    assert s["by_category"]["ui"] == 1
    clear_requests()
