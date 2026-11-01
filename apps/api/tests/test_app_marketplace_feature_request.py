from app.services.app_marketplace_feature_request import create_feature_request, vote, rank_requests

def test_create():
    r = create_feature_request(app_id="a1", user_id="u1", title="Dark mode support", description="Please add dark mode")
    assert r["status"] == "open"
    assert r["votes"] == 1

def test_short_title():
    r = create_feature_request(app_id="a1", user_id="u1", title="Hi", description="D")
    assert r["error"]

def test_vote():
    req = {"votes": 1, "voters": ["u1"]}
    r = vote(request=req, user_id="u2")
    assert r["votes"] == 2

def test_double_vote():
    req = {"votes": 1, "voters": ["u1"]}
    r = vote(request=req, user_id="u1")
    assert r["error"]

def test_rank():
    reqs = [{"title": "A", "votes": 5}, {"title": "B", "votes": 10}, {"title": "C", "votes": 3}]
    ranked = rank_requests(requests=reqs)
    assert ranked[0]["title"] == "B"
