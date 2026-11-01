from app.services.app_marketplace_app_app_feature_request import create_feature_request, build_feature_board

def test_create():
    r = create_feature_request(title="Dark mode", description="Add dark theme", author="Alice")
    assert r["id"].startswith("feat_")
    assert r["status"] == "open"
    assert r["votes"] == 0

def test_board():
    reqs = [
        {"title": "API", "status": "open", "votes": 10},
        {"title": "Dark mode", "status": "open", "votes": 25},
        {"title": "Export", "status": "completed", "votes": 5},
    ]
    r = build_feature_board(requests=reqs)
    assert r["total"] == 3
    assert r["total_votes"] == 40
    assert r["columns"]["open"][0]["title"] == "Dark mode"  # sorted by votes
