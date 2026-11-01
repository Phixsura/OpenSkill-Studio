from app.services.app_marketplace_usage_analytics import UsageAnalytics


def test_record_and_count():
    ua = UsageAnalytics()
    ua.record_event("ext-1", "page_view", user_id="u1")
    ua.record_event("ext-1", "page_view", user_id="u2")
    ua.record_event("ext-1", "api_call", user_id="u1")
    assert ua.get_event_count("ext-1") == 3
    assert ua.get_event_count("ext-1", "page_view") == 2


def test_unique_users_and_orgs():
    ua = UsageAnalytics()
    ua.record_event("ext-2", "use", org_id="o1", user_id="u1")
    ua.record_event("ext-2", "use", org_id="o1", user_id="u2")
    ua.record_event("ext-2", "use", org_id="o2", user_id="u1")
    assert ua.get_unique_users("ext-2") == 2
    assert ua.get_unique_orgs("ext-2") == 2


def test_top_extensions():
    ua = UsageAnalytics()
    for _ in range(5):
        ua.record_event("popular", "use")
    for _ in range(2):
        ua.record_event("niche", "use")
    top = ua.get_top_extensions(limit=5)
    assert top[0][0] == "popular"
    assert top[0][1] == 5


def test_summary():
    ua = UsageAnalytics()
    ua.record_event("ext-3", "install", org_id="o1", user_id="u1")
    ua.record_event("ext-3", "api_call", org_id="o2", user_id="u2")
    summary = ua.get_summary("ext-3")
    assert summary["total_events"] == 2
    assert summary["unique_users"] == 2
    assert "install" in summary["event_types"]
    assert "api_call" in summary["event_types"]


def test_daily_breakdown():
    ua = UsageAnalytics()
    ua.record_event("ext-4", "view")
    ua.record_event("ext-4", "click")
    breakdown = ua.get_daily_breakdown("ext-4")
    assert len(breakdown) >= 1
    assert list(breakdown.values())[0] == 2
