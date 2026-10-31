from app.services.app_marketplace_app_changelog_digest import build_changelog_digest, should_send_digest

def test_digest():
    d = build_changelog_digest(period="Oct 2026",
        app_updates=[{"app_name": "App1", "version": "2.0"}],
        platform_changes=["New API v3"], deprecations=["v1 sunset"])
    assert d["section_count"] == 3
    assert d["total_updates"] == 2

def test_empty():
    d = build_changelog_digest(period="Oct 2026", app_updates=[], platform_changes=[], deprecations=[])
    assert d["section_count"] == 0

def test_should_send():
    assert should_send_digest(subscriber_prefs={"weekly_digest": True}, digest_type="weekly")
    assert not should_send_digest(subscriber_prefs={"weekly_digest": False}, digest_type="weekly")
