from app.services.app_marketplace_app_platform_announcement import create_announcement, filter_announcements

def test_create():
    r = create_announcement(title="New Feature!", content="We launched dark mode.", audience="all", priority="high")
    assert r["announcement_id"].startswith("pann_")
    assert r["priority"] == "high"

def test_xss():
    r = create_announcement(title="<script>xss</script>", content="ok")
    assert "<script>" not in r["title"]

def test_invalid_audience():
    r = create_announcement(title="X", content="Y", audience="nobody")
    assert "error" in r

def test_filter():
    anns = [
        {"audience": "all", "priority": "low"},
        {"audience": "developers", "priority": "urgent"},
        {"audience": "admins", "priority": "normal"},
    ]
    r = filter_announcements(announcements=anns, audience="developers")
    assert r["count"] == 2  # "all" + "developers"
    assert r["announcements"][0]["priority"] == "urgent"  # sorted by priority
