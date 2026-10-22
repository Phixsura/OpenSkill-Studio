from app.services.app_developer_app_status_summary import build_status_summary

def test_summary():
    apps = [{"status": "published"}, {"status": "published"}, {"status": "draft"}, {"status": "rejected"}]
    s = build_status_summary(apps)
    assert s["total"] == 4
    assert s["published_pct"] == 50.0
    assert s["needs_attention"] == 1

def test_empty():
    s = build_status_summary([])
    assert s["total"] == 0
    assert s["published_pct"] == 0
