from app.services.app_marketplace_app_content_scheduler import schedule_content, get_schedule_calendar

def test_schedule():
    r = schedule_content(content_type="changelog", title="v2.0 Release Notes",
        body="New features...", publish_at="2099-01-01T09:00:00", author="alice")
    assert r["schedule_id"].startswith("sched_")
    assert r["status"] == "scheduled"

def test_past_date():
    r = schedule_content(content_type="blog_post", title="X", body="Y",
        publish_at="2020-01-01T00:00:00", author="bob")
    assert "error" in r

def test_invalid_type():
    r = schedule_content(content_type="tweet", title="X", body="Y",
        publish_at="2099-01-01T00:00:00", author="a")
    assert "error" in r

def test_calendar():
    items = [
        {"publish_at": "2099-01-01T09:00:00", "title": "A"},
        {"publish_at": "2099-01-01T14:00:00", "title": "B"},
        {"publish_at": "2099-01-02T10:00:00", "title": "C"},
    ]
    r = get_schedule_calendar(items=items)
    assert r["total_scheduled"] == 3
    assert r["unique_dates"] == 2
