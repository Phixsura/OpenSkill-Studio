from app.services.app_marketplace_app_app_app_app_app_app_app_access_review import create_review, decide, review_summary

def test_review():
    r = create_review("admin", [{"id": "u1", "role": "admin"}, {"id": "u2", "role": "viewer", "last_active_days": 90}])
    assert r["total"] == 2
    d = decide(r, "u1", "approve")
    assert d["decided"]
    assert d["progress"] == 50
    decide(r, "u2", "revoke")
    s = review_summary(r)
    assert s["complete"]
    assert s["by_decision"]["approve"] == 1
    assert s["by_decision"]["revoke"] == 1
