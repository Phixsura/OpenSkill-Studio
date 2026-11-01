from app.services.app_marketplace_app_app_app_app_app_app_app_session_analytics import analyze_sessions

def test_analyze():
    sessions = [
        {"duration_sec": 120, "pages_viewed": 5, "source": "google"},
        {"duration_sec": 30, "pages_viewed": 1, "source": "google"},
        {"duration_sec": 300, "pages_viewed": 12, "source": "direct"},
    ]
    r = analyze_sessions(sessions)
    assert r["total_sessions"] == 3
    assert r["avg_duration_sec"] == 150
    assert r["bounce_rate"] == 33.3
    assert r["top_source"] == "google"

def test_empty():
    r = analyze_sessions([])
    assert r["total_sessions"] == 0
    assert r["bounce_rate"] == 0.0
