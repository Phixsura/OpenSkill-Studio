from app.services.app_marketplace_extension_review_moderation import (
    ReviewModerationService, ModerationStatus, RejectionReason,
)
import pytest


def test_submit_approved():
    svc = ReviewModerationService()
    mod = svc.submit_review("r1", "ext-1", "u1", "Great extension, really useful!", 5)
    assert mod.status == ModerationStatus.APPROVED
    assert len(mod.auto_flags) == 0


def test_spam_flagged():
    svc = ReviewModerationService()
    mod = svc.submit_review("r2", "ext-1", "u2",
                            "Buy now click here free money get rich!", 5)
    assert mod.status == ModerationStatus.FLAGGED
    assert "spam_pattern" in mod.auto_flags


def test_rating_validation():
    svc = ReviewModerationService()
    with pytest.raises(ValueError, match="1-5"):
        svc.submit_review("r3", "ext-1", "u1", "Good extension", 6)


def test_too_short():
    svc = ReviewModerationService()
    with pytest.raises(ValueError, match="too short"):
        svc.submit_review("r4", "ext-1", "u1", "Bad", 1)


def test_moderate_reject():
    svc = ReviewModerationService()
    mod = svc.submit_review("r5", "ext-1", "u1", "This is a valid review content", 3)
    svc.moderate(mod.moderation_id, "mod-1", ModerationStatus.REJECTED,
                 RejectionReason.OFF_TOPIC)
    assert mod.status == ModerationStatus.REJECTED


def test_self_moderate_blocked():
    svc = ReviewModerationService()
    mod = svc.submit_review("r6", "ext-1", "u1", "Valid review here indeed", 4)
    with pytest.raises(PermissionError, match="own review"):
        svc.moderate(mod.moderation_id, "u1", ModerationStatus.APPROVED)


def test_appeal_flow():
    svc = ReviewModerationService()
    mod = svc.submit_review("r7", "ext-1", "u1", "Legitimate review content here", 2)
    svc.moderate(mod.moderation_id, "mod-1", ModerationStatus.REJECTED,
                 RejectionReason.LOW_QUALITY)
    assert svc.appeal(mod.moderation_id, "u1", "This was a genuine review") is True
    assert mod.status == ModerationStatus.APPEALED
