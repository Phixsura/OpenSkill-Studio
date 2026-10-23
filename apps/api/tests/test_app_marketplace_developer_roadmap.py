from app.services.app_marketplace_developer_roadmap import get_roadmap, vote_on_feature

def test_roadmap():
    r = get_roadmap()
    assert r["total_items"] >= 6
    assert r["in_progress_count"] == 2
    assert r["completed_count"] >= 1

def test_vote():
    votes = {"r1": 10}
    r = vote_on_feature(feature_id="r1", user_id="u1", votes=votes)
    assert r["votes"] == 11
    assert r["voted"]
