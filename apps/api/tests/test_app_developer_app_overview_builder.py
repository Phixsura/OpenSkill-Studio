from app.services.app_developer_app_overview_builder import build_app_overview

def test_overview():
    o = build_app_overview(
        app={"name": "X", "webhook_url": "https://x.com", "manifest": {"sandbox": {"runtime": "python3.12"}, "ui_extensions": [{"surface": "card"}]}},
        version={"version": "2.0", "review_status": "approved"},
        stats={"installs": 50}, health={"score": 95},
        permissions=["read:cohorts"], badges=[{"label": "Popular"}])
    assert o["current_version"] == "2.0"
    assert o["has_sandbox"] is True
    assert o["has_webhook"] is True
    assert o["has_ui_extensions"] is True
    assert o["badge_count"] == 1

def test_no_version():
    o = build_app_overview(app={}, version=None, stats={}, health={}, permissions=[], badges=[])
    assert o["current_version"] is None
