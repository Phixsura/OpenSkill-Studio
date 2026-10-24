from app.services.app_developer_app_summary_builder import build_app_summary_list

def test_list():
    apps = [{"id": "a1", "name": "X", "slug": "x", "status": "published", "category": "connector", "install_count": 42, "health_score": 95}]
    s = build_app_summary_list(apps)
    assert len(s) == 1
    assert s[0]["needs_attention"] is False

def test_attention():
    apps = [{"id": "a", "status": "rejected", "health_score": 60}]
    s = build_app_summary_list(apps)
    assert s[0]["needs_attention"] is True
