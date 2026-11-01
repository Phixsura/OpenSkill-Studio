from app.services.app_marketplace_app_app_app_app_app_app_app_dev_roadmap import build_roadmap, vote_item

def test_roadmap():
    r = build_roadmap([
        {"id": "r1", "title": "SSO Support", "status": "in_progress", "votes": 42, "quarter": "Q4 2026"},
        {"id": "r2", "title": "GraphQL API", "status": "planned", "votes": 85, "tags": ["api"]},
        {"id": "r3", "title": "Dark Mode", "status": "shipped", "votes": 120},
    ])
    assert r["total_items"] == 3
    assert len(r["columns"]["planned"]) == 1
    assert r["columns"]["planned"][0]["title"] == "GraphQL API"

def test_vote():
    items = [{"id": "r1", "votes": 10}]
    r = vote_item(items, "r1")
    assert r["votes"] == 11
