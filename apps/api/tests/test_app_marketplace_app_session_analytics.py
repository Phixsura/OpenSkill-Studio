from app.services.app_marketplace_app_session_analytics import compute_session_metrics, group_sessions_by_source

def test_metrics():
    sessions = [{"duration_s": 120, "page_views": 5}, {"duration_s": 30, "page_views": 1},
                {"duration_s": 300, "page_views": 10}]
    r = compute_session_metrics(sessions=sessions)
    assert r["total"] == 3
    assert r["bounce_rate"] > 30

def test_empty():
    r = compute_session_metrics(sessions=[])
    assert r["total"] == 0

def test_by_source():
    sessions = [{"source": "organic"}, {"source": "organic"}, {"source": "referral"}, {"source": "direct"}]
    r = group_sessions_by_source(sessions=sessions)
    assert r[0]["source"] == "organic"
    assert r[0]["count"] == 2
