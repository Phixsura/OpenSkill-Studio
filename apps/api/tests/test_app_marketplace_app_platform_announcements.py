from app.services.app_marketplace_app_platform_announcements import create_announcement, get_active_announcements

def test_create():
    a = create_announcement(title="API v3 Released", body="Check out the new features", type="feature")
    assert a["type"] == "feature"

def test_invalid():
    a = create_announcement(title="X", body="Y", type="urgent")
    assert a["error"]

def test_pinned_first():
    anns = [{"title": "Regular", "pinned": False}, {"title": "Important", "pinned": True}]
    r = get_active_announcements(announcements=anns)
    assert r[0]["title"] == "Important"
