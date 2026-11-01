from app.services.app_marketplace_extension_content_moderation import (
    ContentModerationService, ContentType, ModerationAction,
)


def test_approve_clean():
    cms = ContentModerationService()
    result = cms.screen("c1", ContentType.NAME, "My Awesome Extension")
    assert result.action == ModerationAction.APPROVE
    assert len(result.reasons) == 0


def test_reject_blocked():
    cms = ContentModerationService()
    result = cms.screen("c2", ContentType.DESCRIPTION, "This extension helps you hack systems")
    assert result.action == ModerationAction.REJECT
    assert any("hack" in r for r in result.reasons)


def test_flag_suspicious():
    cms = ContentModerationService()
    result = cms.screen("c3", ContentType.REVIEW, "Act now for free money!")
    assert result.action == ModerationAction.FLAG
    assert "c3" in cms.get_queue()


def test_manual_override():
    cms = ContentModerationService()
    cms.screen("c4", ContentType.DESCRIPTION, "Check this hack tip")
    cms.manual_review("c4", ModerationAction.APPROVE, "admin-1", "False positive")
    result = cms.get_result("c4")
    assert result.action == ModerationAction.APPROVE
    assert result.moderator == "admin-1"


def test_queue_clears_after_review():
    cms = ContentModerationService()
    cms.screen("c5", ContentType.REVIEW, "Guaranteed results, act now!")
    assert "c5" in cms.get_queue()
    cms.manual_review("c5", ModerationAction.REJECT, "mod")
    assert "c5" not in cms.get_queue()


def test_stats():
    cms = ContentModerationService()
    cms.screen("s1", ContentType.NAME, "Good Extension")
    cms.screen("s2", ContentType.NAME, "Spam scam malware")
    cms.screen("s3", ContentType.REVIEW, "Click here for free money")
    stats = cms.get_stats()
    assert stats["total_screened"] == 3
    assert stats["by_action"]["approve"] == 1
    assert stats["by_action"]["reject"] == 1
    assert stats["pending_review"] == 1
