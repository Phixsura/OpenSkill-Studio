from app.services.app_marketplace_app_feature_announcement import create_announcement, get_whats_new

def test_create():
    r = create_announcement(title="Dark Mode!", body="We added dark mode support.",
        feature_tag="ui", cta_label="Try it", cta_url="/settings/theme")
    assert r["announcement_id"].startswith("ann_")
    assert r["cta"]["label"] == "Try it"

def test_no_cta():
    r = create_announcement(title="Bug fix", body="Fixed crash", feature_tag="stability")
    assert r["cta"] is None

def test_whats_new():
    announcements = [
        {"published_at": "2026-10-22T00:00:00", "title": "Old"},
        {"published_at": "2026-10-23T12:00:00", "title": "New"},
    ]
    r = get_whats_new(announcements=announcements, last_seen="2026-10-23T00:00:00")
    assert r["new_count"] == 1
    assert r["has_unread"]

def test_whats_new_all():
    r = get_whats_new(announcements=[{"title": "A"}, {"title": "B"}])
    assert r["new_count"] == 2
